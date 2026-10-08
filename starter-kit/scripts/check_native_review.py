#!/usr/bin/env python3
"""Validate a scoped native review inventory against actual local source/Evidence bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from check_task_execution import HEX40, HEX64, evidence, read_json, relative, require, text, validate_format

AREAS = {'memory', 'numeric', 'ownership', 'concurrency', 'units'}


def validate(record, root, expected_candidate, required_paths):
    validate_format(record, 'native-review.schema.json')
    require(isinstance(record, dict) and type(record.get('schema_version')) is int and record.get('schema_version') == 1, 'unsupported native review record')
    require(HEX40.fullmatch(expected_candidate) and record.get('candidate') == expected_candidate, 'native review candidate mismatch')
    require(isinstance(required_paths, list) and required_paths and len(required_paths) == len(set(required_paths)), 'reviewed scope must be nonempty/unique')
    ids = evidence(record.get('evidence'), root)
    inventory = record.get('inventory')
    require(isinstance(inventory, list) and inventory, 'missing native review scope')
    paths, gaps, failed = set(), [], False
    root = root.resolve()
    for item in inventory:
        require(isinstance(item, dict) and text(item.get('path')) and item['path'] not in paths, 'duplicate/missing source path')
        paths.add(item['path'])
        source = root / relative(item['path'])
        cursor = root
        for part in relative(item['path']).parts:
            cursor /= part
            require(not cursor.is_symlink(), 'symlink source prohibited')
        require(source.is_file() and source.resolve().is_relative_to(root) and source.stat().st_size <= 10_000_000, 'source missing/oversized')
        require(HEX64.fullmatch(str(item.get('sha256', ''))) and hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256'], 'native source changed after review')
        require(item.get('status') in {'REVIEWED', 'UNREVIEWED', 'BLOCKED'} and text(item.get('basis')), 'review status/basis missing')
        if item['status'] != 'REVIEWED':
            gaps.append(item['path'])
        else:
            areas = item.get('areas')
            require(isinstance(areas, dict) and set(areas) == AREAS, 'native review areas incomplete')
            for area in areas.values():
                require(isinstance(area, dict) and area.get('status') in {'PASS', 'FAIL', 'BLOCKED', 'NOT_RUN', 'NOT_APPLICABLE'} and text(area.get('basis')), 'review area lacks result/basis')
                if area['status'] == 'PASS':
                    refs = area.get('evidence_ids')
                    require(isinstance(refs, list) and refs and all(ids.get(x) == expected_candidate for x in refs), 'native review Evidence missing/stale')
                elif area['status'] not in {'NOT_APPLICABLE'}:
                    gaps.append(item['path'])
                    failed = failed or area['status'] == 'FAIL'
    require(set(required_paths) == paths, 'scope omitted or unexpectedly expanded')
    units = record.get('unit_contracts')
    require(isinstance(units, list), 'unit inventory missing')
    for unit in units:
        require(isinstance(unit, dict) and text(unit.get('quantity')) and text(unit.get('input_unit')) and text(unit.get('output_unit')) and text(unit.get('conversion')) and text(unit.get('invariant')), 'incomplete dimensional contract')
        refs = unit.get('evidence_ids')
        require(isinstance(refs, list) and refs and all(ids.get(x) == expected_candidate for x in refs), 'dimensional Evidence missing/stale')
    if any(item.get('areas', {}).get('units', {}).get('status') == 'PASS' for item in inventory):
        require(units, 'units PASS without dimensional contract')
    return {'status': 'FAIL' if failed else 'BLOCKED' if gaps else 'PASS', 'scope': 'native-review-record-consistency',
            'candidate': expected_candidate, 'reviewed_paths': len(paths) - len(set(gaps)),
            'unreviewed_paths': sorted(set(gaps)), 'sdk_certified': False, 'host_certified': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record', type=Path, required=True)
    p.add_argument('--evidence-root', type=Path, required=True)
    p.add_argument('--expected-candidate', required=True)
    p.add_argument('--required-path', action='append', required=True)
    args = p.parse_args()
    try:
        report = validate(read_json(args.record), args.evidence_root, args.expected_candidate, args.required_path)
        print(json.dumps(report))
        return 0 if report['status'] == 'PASS' else 1
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'FAIL', 'scope': 'native-review-record-consistency', 'error': str(exc), 'sdk_certified': False, 'host_certified': False}))
        return 1

if __name__ == '__main__':
    sys.exit(main())
