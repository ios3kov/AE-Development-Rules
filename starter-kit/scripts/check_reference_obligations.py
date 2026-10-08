#!/usr/bin/env python3
"""Conditional reference Evidence adapter. Never executes candidate commands."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

RANK = {"static": 0, "unit": 1, "integration": 2, "runtime": 3, "packaged-process": 4, "host": 5, "device": 5}
CASES = {"positive", "negative", "malformed", "boundary", "cancellation", "recovery"}
HEX = re.compile(r"^[0-9a-f]{64}$")
REV = re.compile(r"^[0-9a-f]{40}$")

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()

def load_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("non-finite JSON number")))

def text(value):
    return isinstance(value, str) and bool(value.strip())

def strings(value):
    return isinstance(value, list) and bool(value) and all(text(x) for x in value) and len(set(value)) == len(value)

def timestamp(value):
    try:
        if not isinstance(value, str) or not value.endswith("Z"):
            return None
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None

def adequate(actual, needed):
    if not isinstance(actual, str) or not isinstance(needed, str) or actual not in RANK or needed not in RANK:
        return False
    if needed in {"host", "device"}:
        return actual == needed
    return RANK[actual] >= RANK[needed]

def contained_file(root, relative):
    if not text(relative) or "\\" in relative or ":" in relative:
        raise ValueError("invalid relative path")
    rel = pathlib.PurePosixPath(relative)
    if rel.is_absolute() or any(part in {"..", "."} for part in relative.split("/")):
        raise ValueError("unsafe relative path")
    base = pathlib.Path(root).resolve(strict=True)
    path = base / rel
    # Refuse symlinks even when their current destination is inside the checkout.
    cursor = base
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("symlink evidence path")
    path = path.resolve(strict=True)
    if not path.is_relative_to(base) or not path.is_file():
        raise ValueError("evidence outside root or not a file")
    return path

def evidence_integrity(record, root):
    if not isinstance(record, dict) or not isinstance(record.get("artifact_sha256"), str) or not HEX.fullmatch(record["artifact_sha256"]):
        return False
    try:
        return hashlib.sha256(contained_file(root, record.get("artifact_path")).read_bytes()).hexdigest() == record["artifact_sha256"]
    except (OSError, RuntimeError, ValueError, TypeError):
        return False

def policy_errors(policy):
    if not isinstance(policy, dict):
        return ["trusted reference policy required"]
    errors = []
    if type(policy.get("schema_version")) is not int or policy["schema_version"] != 1 or type(policy.get("reference_triggered")) is not bool:
        errors.append("invalid policy version/trigger")
    if policy.get("reference_triggered") is not True:
        return errors
    if not isinstance(policy.get("candidate_revision"), str) or not REV.fullmatch(policy["candidate_revision"]):
        errors.append("policy candidate must be exact Git SHA")
    if not isinstance(policy.get("reference_sha256"), str) or not HEX.fullmatch(policy["reference_sha256"]):
        errors.append("invalid policy reference digest")
    items = policy.get("obligations")
    if not isinstance(items, list) or not items:
        return errors + ["policy obligations missing"]
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not text(item.get("id")):
            errors.append("invalid policy obligation")
            continue
        if item["id"] in seen:
            errors.append("duplicate policy obligation")
        seen.add(item["id"])
        if type(item.get("required")) is not bool:
            errors.append("invalid policy required flag")
        if item.get("required") is False:
            if not text(item.get("exclusion_reason")) or not text(item.get("decision_ref")):
                errors.append("excluded obligation needs reason and decision")
        elif not strings(item.get("required_cases")) or any(c not in CASES for c in item["required_cases"]):
            errors.append("invalid policy case minimum")
        if not strings(item.get("requirement_ids")) or not text(item.get("check_id")):
            errors.append("policy must bind existing requirements/check")
        if not isinstance(item.get("required_authority"), str) or item["required_authority"] not in RANK:
            errors.append("invalid policy authority")
    return errors

def validate(data, evidence_root=None, policy=None, expected_revision=None, candidate_root=None):
    # Legacy local use may keep source and reports together; enforced review
    # supplies the immutable source checkout independently of Evidence storage.
    owner_root = candidate_root if candidate_root is not None else evidence_root
    errors = policy_errors(policy)
    if not isinstance(data, dict):
        return errors + ["ledger root must be object"]
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1 or type(data.get("reference_triggered")) is not bool:
        errors.append("invalid ledger version/trigger")
    if errors:
        return errors
    if data["reference_triggered"] != policy["reference_triggered"]:
        return ["reference trigger differs from trusted policy"]
    if not policy["reference_triggered"]:
        return []
    revision = data.get("candidate_revision")
    if revision != policy["candidate_revision"] or (expected_revision is not None and revision != expected_revision):
        errors.append("candidate differs from trusted policy/checkout")
    ref = data.get("reference")
    if not isinstance(ref, dict) or not text(ref.get("name")) or not text(ref.get("version")) or ref.get("sha256") != policy["reference_sha256"]:
        errors.append("reference identity differs from policy or incomplete")
    if evidence_root is None:
        errors.append("triggered reference requires evidence root")
    inventory = data.get("inventory")
    expected = {item["id"]: item for item in policy["obligations"]}
    if not strings(inventory) or set(inventory) != set(expected):
        errors.append("inventory differs from trusted coverage")
    items = data.get("obligations")
    if not isinstance(items, list) or not items:
        return errors + ["obligations missing"]
    seen, evidence_ids = set(), set()
    for item in items:
        if not isinstance(item, dict) or not text(item.get("id")):
            errors.append("invalid obligation")
            continue
        ident = item["id"]
        if ident in seen or ident not in expected:
            errors.append(ident + ": duplicate or unexpected obligation")
            continue
        seen.add(ident)
        minimum = expected[ident]
        if type(item.get("required")) is not bool:
            errors.append(ident + ": required must be boolean")
        for field in ("required", "required_cases", "required_authority", "requirement_ids", "check_id"):
            if item.get(field) != minimum.get(field):
                errors.append(ident + ": policy mismatch " + field)
        if minimum["required"] is False:
            if item.get("status") != "NOT_APPLICABLE" or item.get("exclusion_reason") != minimum["exclusion_reason"] or item.get("decision_ref") != minimum["decision_ref"]:
                errors.append(ident + ": invalid reviewed exclusion")
            continue
        if item.get("status") != "PASS":
            errors.append(ident + ": required obligation not PASS")
        owner = item.get("owner")
        if not isinstance(owner, dict) or not text(owner.get("path")) or owner.get("revision") != revision:
            errors.append(ident + ": implementation owner missing/stale")
        elif owner_root is not None and not evidence_integrity({"artifact_path": owner["path"], "artifact_sha256": owner.get("sha256")}, owner_root):
            errors.append(ident + ": implementation owner hash/path failure")
        for field in ("contradictions", "residual_unknowns"):
            if item.get(field) != []:
                errors.append(ident + ": unresolved or missing " + field)
        records = []
        for role in ("original_cases", "fixtures"):
            collection = item.get(role)
            if not isinstance(collection, list):
                errors.append(ident + ": invalid " + role)
                continue
            kinds = [r.get("kind") for r in collection if isinstance(r, dict)]
            if len(kinds) != len(collection) or any(not isinstance(k, str) for k in kinds) or sorted(kinds) != sorted(minimum["required_cases"]):
                errors.append(ident + ": missing/duplicate/unexpected cases in " + role)
            records.extend((role, r) for r in collection)
        records.append(("verifier", item.get("verifier")))
        for role, record in records:
            if not isinstance(record, dict):
                errors.append(ident + ": malformed Evidence")
                continue
            eid = record.get("evidence_id")
            if not text(eid) or eid in evidence_ids:
                errors.append(ident + ": missing/duplicate Evidence ID")
            else:
                evidence_ids.add(eid)
            if evidence_root is not None and not evidence_integrity(record, evidence_root):
                errors.append(ident + ": Evidence hash/path failure")
            if record.get("status") != "PASS" or not text(record.get("environment")) or not text(record.get("command")) or not text(record.get("tool_version")) or not text(record.get("run_id")):
                errors.append(ident + ": incomplete execution Evidence")
            when = timestamp(record.get("observed_at"))
            if when is None or when > datetime.now(timezone.utc):
                errors.append(ident + ": invalid observation timestamp")
            needed = minimum["required_authority"] if role in {"verifier", "original_cases"} else "static"
            if not adequate(record.get("authority"), needed):
                errors.append(ident + ": insufficient/incomparable authority")
            if role == "original_cases":
                if record.get("reference_sha256") != policy["reference_sha256"] or record.get("claim_status") not in {"PROVEN", "OBSERVED"}:
                    errors.append(ident + ": unobserved or substituted reference")
            elif record.get("revision") != revision:
                errors.append(ident + ": stale candidate Evidence")
            if role == "verifier" and (record.get("check_id") != minimum["check_id"] or record.get("requirement_ids") != minimum["requirement_ids"]):
                errors.append(ident + ": verifier must bind existing check/requirements")
            if role == "verifier" and evidence_root is not None and evidence_integrity(record, evidence_root):
                try:
                    report = load_json(contained_file(evidence_root, record["artifact_path"]))
                    fields = {"status": "PASS", "revision": revision, "obligation_id": ident,
                              "check_id": minimum["check_id"], "requirement_ids": minimum["requirement_ids"],
                              "authority": record.get("authority"), "environment": record.get("environment")}
                    if not isinstance(report, dict) or any(report.get(k) != v for k, v in fields.items()) or report.get("case_results") != {case: "PASS" for case in minimum["required_cases"]}:
                        errors.append(ident + ": verifier report failed/incomplete or wrong subject")
                except (OSError, ValueError, TypeError, RuntimeError):
                    errors.append(ident + ": verifier artifact must be typed JSON result")
    if seen != set(expected):
        errors.append("missing policy obligations")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    parser.add_argument("--evidence-root", type=pathlib.Path)
    parser.add_argument("--candidate-root", type=pathlib.Path, help="source checkout; defaults to evidence root for local use")
    parser.add_argument("--policy", type=pathlib.Path, required=True)
    parser.add_argument("--expected-candidate-revision")
    args = parser.parse_args()
    try:
        errors = validate(load_json(args.ledger), args.evidence_root, load_json(args.policy), args.expected_candidate_revision, args.candidate_root)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"status": "FAIL" if errors else "PASS", "scope": "reference-ledger-consistency", "parity_certified": False, "errors": errors}, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
