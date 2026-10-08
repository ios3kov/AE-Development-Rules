#!/usr/bin/env python3
"""Compare candidate evidence to a separately controlled, pinned witness manifest.

The caller must provision the witness manifest and expected digest from a trusted
source outside candidate control. This verifies attestation matching, not truth.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def verify(ledger, manifest, expected_digest):
    errors = []
    if hashlib.sha256(canonical(manifest)).hexdigest() != expected_digest:
        errors.append("protected manifest digest mismatch")
    if manifest.get("schema_version") != 1 or manifest.get("candidate_revision") != ledger.get("candidate_revision"):
        errors.append("manifest version or candidate mismatch")
    reference = ledger.get("reference")
    if not isinstance(reference, dict) or manifest.get("reference_sha256") != reference.get("sha256"):
        errors.append("reference identity mismatch")
    captures = manifest.get("captures")
    if not isinstance(captures, list):
        return errors + ["captures missing"]
    by_id = {}
    for capture in captures:
        if not isinstance(capture, dict) or not capture.get("evidence_id"):
            errors.append("invalid protected capture")
            continue
        ident = capture["evidence_id"]
        if ident in by_id:
            errors.append("duplicate protected capture " + ident)
        by_id[ident] = capture
    for obligation in ledger.get("obligations", []):
        if not isinstance(obligation, dict) or obligation.get("required") is not True:
            continue
        records = obligation.get("original_cases", []) + obligation.get("fixtures", []) + [obligation.get("verifier")]
        for record in records:
            if not isinstance(record, dict):
                errors.append("malformed evidence record")
                continue
            witness = by_id.get(record.get("evidence_id"))
            if not witness:
                errors.append("unwitnessed evidence " + str(record.get("evidence_id")))
                continue
            for field in ("artifact_sha256", "artifact_path"):
                if witness.get(field) != record.get(field):
                    errors.append("witness " + field + " mismatch")
            if not all(witness.get(k) for k in ("run_id", "runner_id", "observed_at", "authority")):
                errors.append("incomplete witness provenance")
            if witness.get("review_status") != "APPROVED":
                errors.append("unapproved witness")
            if record is obligation.get("verifier") and witness.get("revision") != ledger.get("candidate_revision"):
                errors.append("stale witness verifier")
    return errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("ledger")
    p.add_argument("--protected-manifest", type=Path, required=True)
    p.add_argument("--expected-manifest-sha256", required=True)
    args = p.parse_args()
    try:
        ledger = json.loads(Path(args.ledger).read_text())
        manifest = json.loads(args.protected_manifest.read_text())
        errors = verify(ledger, manifest, args.expected_manifest_sha256)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"status": "FAIL" if errors else "PASS", "errors": errors}))
    return bool(errors)

if __name__ == "__main__":
    sys.exit(main())
