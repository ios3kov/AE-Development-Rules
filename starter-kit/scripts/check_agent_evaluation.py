#!/usr/bin/env python3
"""Validate observer evaluation records sealed by an independent expected digest.

Digest custody/authenticity uses existing Evidence/trusted witness governance;
this consistency check cannot authenticate a provider or certify a live agent.
"""
import argparse
import json
from pathlib import Path
import sys
from agent_evaluation import digest, load_json, compare_runs, require


def validate_record(path, expected_sha256):
    raw = Path(path).read_bytes()
    require(digest(raw) == expected_sha256, 'protected observer record digest mismatch')
    record = load_json(path)
    require(record.get('schema_version') == 1 and isinstance(record.get('runs'), list), 'observer record v1 required')
    actual = compare_runs(record['runs'])
    require(record.get('comparison') == actual, 'comparison differs from actual observer records')
    return {'status': actual['status'] if actual['status'] in {'FAIL','BLOCKED'} else 'PASS', 'record_consistency': 'PASS', 'scope': 'sealed-observer-record-consistency', 'run_status': actual['status'],
            'live_agent_status': actual['live_agent_status'], 'ae_host_status': 'NOT_RUN', 'identity_authenticated': False,
            'effectiveness_certified': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record', required=True); p.add_argument('--expected-sha256', required=True)
    a = p.parse_args()
    try:
        result = validate_record(a.record, a.expected_sha256)
        print(json.dumps(result)); return 0 if result['status'] == 'PASS' else 1
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'FAIL', 'scope': 'sealed-observer-record-consistency', 'error': str(exc)})); return 1


if __name__ == '__main__':
    sys.exit(main())
