#!/usr/bin/env python3
"""Fail-closed, conditional reference parity obligation validator."""
import argparse
import json
import hashlib
import re
import pathlib
import sys

RANK = {"static": 0, "unit": 1, "integration": 2, "runtime": 3, "packaged-process": 4, "host": 5, "device": 5}
CASES = {"positive", "negative", "malformed", "boundary", "cancellation", "recovery"}

HEX = re.compile(r"^[0-9a-fA-F]{64}$")

def evidence_integrity(record, root):
    if not isinstance(record, dict):
        return False
    relative = record.get("artifact_path")
    digest = record.get("artifact_sha256")
    if not isinstance(relative, str) or not relative or not isinstance(digest, str) or not HEX.fullmatch(digest):
        return False
    try:
        base = root.resolve(strict=True)
        path = (base / relative).resolve(strict=True)
        if not path.is_relative_to(base) or not path.is_file():
            return False
        return hashlib.sha256(path.read_bytes()).hexdigest() == digest.lower()
    except (OSError, RuntimeError, ValueError):
        return False

def validate(data, evidence_root=None):
    errors = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if data.get("reference_triggered") is not True:
        return errors if data.get("reference_triggered") is False else errors + ["reference_triggered must be boolean"]
    if evidence_root is None:
        errors.append("triggered reference requires --evidence-root")
    if not isinstance(data.get("candidate_revision"), str) or not data.get("candidate_revision"):
        errors.append("candidate_revision missing")
    if not isinstance(data.get("reference"), dict) or not all(data["reference"].get(k) for k in ("name", "version", "sha256")) or (isinstance(data.get("reference"), dict) and not HEX.fullmatch(str(data["reference"].get("sha256", "")))):
        errors.append("reference identity incomplete")
    inventory = data.get("inventory")
    if not isinstance(inventory, list) or not inventory or any(not isinstance(x, str) or not x for x in inventory) or len(set(inventory)) != len(inventory):
        errors.append("inventory must contain unique behavior IDs")
    obligations = data.get("obligations")
    if not isinstance(obligations, list) or not obligations:
        return errors + ["triggered reference requires obligations"]
    seen = set()
    for index, o in enumerate(obligations):
        prefix = "obligations[%d]" % index
        if not isinstance(o, dict):
            errors.append(prefix + " must be object")
            continue
        ident = o.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            errors.append(prefix + " missing or duplicate id")
        else:
            seen.add(ident)
        if o.get("required") is not True:
            if o.get("required") is not False:
                errors.append(prefix + " required must be boolean")
            continue
        if o.get("status") != "PASS":
            errors.append(prefix + " required obligation not PASS")
            continue
        owner = o.get("owner")
        if not isinstance(owner, dict) or not all(owner.get(k) for k in ("path", "revision")):
            errors.append(prefix + " missing implementation owner/revision")
        elif owner["revision"] != data.get("candidate_revision"):
            errors.append(prefix + " stale owner revision")
        required_cases = o.get("required_cases")
        if not isinstance(required_cases, list) or not required_cases or any(c not in CASES for c in required_cases) or len(set(required_cases)) != len(required_cases):
            errors.append(prefix + " invalid required_cases")
            continue
        originals = o.get("original_cases", [])
        fixtures = o.get("fixtures", [])
        if not isinstance(originals, list) or not isinstance(fixtures, list):
            errors.append(prefix + " invalid case collections")
            continue
        for case in required_cases:
            for label, collection in (("original_cases", originals), ("fixtures", fixtures)):
                matches = [v for v in collection if isinstance(v, dict) and v.get("kind") == case and v.get("evidence_id") and v.get("artifact_sha256")]
                if len(matches) != 1:
                    errors.append(prefix + " " + label + " missing/ambiguous " + case)
        if o.get("required_authority") not in RANK:
            errors.append(prefix + " unknown required authority")
        if evidence_root is not None:
            for label, collection in (("original_cases", originals), ("fixtures", fixtures)):
                for record in collection:
                    if not evidence_integrity(record, pathlib.Path(evidence_root)):
                        errors.append(prefix + " " + label + " evidence integrity failure")
        verifier = o.get("verifier")
        if not isinstance(verifier, dict) or not all(verifier.get(k) for k in ("command", "evidence_id", "artifact_sha256")):
            errors.append(prefix + " verifier evidence missing")
            continue
        if evidence_root is not None and not evidence_integrity(verifier, pathlib.Path(evidence_root)):
            errors.append(prefix + " verifier evidence integrity failure")
        if verifier.get("authority") not in RANK:
            errors.append(prefix + " unknown verifier authority")
        if verifier.get("status") != "PASS" or verifier.get("revision") != data.get("candidate_revision"):
            errors.append(prefix + " verifier failed or stale")
        needed = o.get("required_authority")
        actual = verifier.get("authority")
        if needed not in RANK or actual not in RANK or RANK[actual] < RANK[needed]:
            errors.append(prefix + " insufficient verifier authority")
        if o.get("contradictions") or o.get("residual_unknowns"):
            errors.append(prefix + " unresolved contradictions/unknowns")
    if isinstance(inventory, list) and all(isinstance(x, str) for x in inventory):
        missing = set(inventory) - seen
        unexpected = seen - set(inventory)
        if missing:
            errors.append("unmapped inventory behaviors: " + ", ".join(sorted(missing)))
        if unexpected:
            errors.append("obligations absent from inventory: " + ", ".join(sorted(unexpected)))
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    parser.add_argument("--evidence-root", type=pathlib.Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(pathlib.Path(args.ledger).read_text(encoding="utf-8")), args.evidence_root)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({"status": "FAIL" if errors else "PASS", "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
