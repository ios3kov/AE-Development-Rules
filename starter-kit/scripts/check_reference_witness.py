#!/usr/bin/env python3
"""Pinned witness + policy + local Evidence validation using trusted code only."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
from check_reference_obligations import canonical, load_json, validate, timestamp, text, HEX, contained_file

def verify(ledger, manifest, expected_digest, evidence_root=None, expected_revision=None, now=None, candidate_root=None):
    if not isinstance(manifest, dict):
        return ["protected manifest must be object"]
    if not isinstance(expected_digest, str) or not HEX.fullmatch(expected_digest):
        return ["invalid externally pinned manifest digest"]
    if hashlib.sha256(canonical(manifest)).hexdigest() != expected_digest:
        return ["protected manifest digest mismatch"]
    errors = validate(ledger, evidence_root, manifest.get("policy"), expected_revision, candidate_root)
    if errors:
        return errors
    if not ledger["reference_triggered"]:
        return ["witness review requires triggered reference"]
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        errors.append("invalid manifest schema")
    current = now or datetime.now(timezone.utc)
    reviewed, expires = timestamp(manifest.get("reviewed_at")), timestamp(manifest.get("expires_at"))
    if reviewed is None or expires is None or not reviewed <= current < expires:
        errors.append("witness review expired or invalid")
    reviewer = manifest.get("reviewer_id")
    if not text(reviewer) or manifest.get("review_status") != "APPROVED":
        errors.append("independent reviewer approval missing")
    captures = manifest.get("captures")
    if not isinstance(captures, list):
        return errors + ["protected captures missing"]
    by_id = {}
    for capture in captures:
        if not isinstance(capture, dict) or not text(capture.get("evidence_id")):
            errors.append("invalid protected capture")
            continue
        ident = capture["evidence_id"]
        if ident in by_id:
            errors.append("duplicate protected capture")
        by_id[ident] = capture
    used = set()
    for obligation in ledger["obligations"]:
        if not obligation["required"]:
            continue
        records = [(role, record) for role in ("original_cases", "fixtures") for record in obligation[role]]
        records.append(("verifier", obligation["verifier"]))
        for role, record in records:
            eid = record["evidence_id"]
            used.add(eid)
            witness = by_id.get(eid)
            if witness is None:
                errors.append("unwitnessed Evidence " + eid)
                continue
            # Covers role, case, environment, authority, run/time, subject and procedure;
            # byte hashes alone cannot prevent reusing a capture for another scenario.
            expected = {"obligation_id": obligation["id"], "role": role,
                        "record_sha256": hashlib.sha256(canonical(record)).hexdigest()}
            if any(witness.get(k) != v for k, v in expected.items()):
                errors.append("capture binding mismatch " + eid)
            if not text(witness.get("runner_id")) or witness.get("runner_id") == reviewer:
                errors.append("missing runner or self-approved capture " + eid)
            if witness.get("review_status") != "APPROVED":
                errors.append("unapproved capture " + eid)
            observed = timestamp(record["observed_at"])
            if reviewed is not None and observed > reviewed:
                errors.append("capture observed after approval " + eid)
    if used != set(by_id):
        errors.append("protected capture coverage mismatch")
    return errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("ledger", type=Path)
    p.add_argument("--protected-manifest", type=Path, required=True)
    p.add_argument("--expected-manifest-sha256", required=True)
    p.add_argument("--evidence-root", type=Path, required=True)
    p.add_argument("--candidate-root", type=Path, help="immutable source checkout; defaults to evidence root for local use")
    p.add_argument("--expected-candidate-revision", required=True)
    args = p.parse_args()
    try:
        relative = args.ledger.absolute().relative_to(args.evidence_root.absolute()).as_posix()
        ledger_path = contained_file(args.evidence_root, relative)
        errors = verify(load_json(ledger_path), load_json(args.protected_manifest),
                        args.expected_manifest_sha256, args.evidence_root, args.expected_candidate_revision, candidate_root=args.candidate_root)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        errors = [str(exc)]
    # Never echo protected witness or candidate-controlled diagnostics.
    print(json.dumps({"status": "FAIL" if errors else "PASS", "scope": "pinned-reference-evidence-consistency",
                      "parity_certified": False, "error_count": len(errors)}))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
