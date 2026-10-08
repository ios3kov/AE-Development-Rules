#!/usr/bin/env python3
"""Conditional task/review record checks. No execution, lock, authorization or host certificate."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
STATUSES = {'PASS', 'FAIL', 'BLOCKED', 'NOT_RUN'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def relative(value):
    require(text(value) and '\\' not in value and ':' not in value, 'invalid relative path')
    p = PurePosixPath(value)
    require(not p.is_absolute() and all(x not in {'', '.', '..'} for x in value.split('/')), 'unsafe path')
    return p


def overlaps(left, right):
    a, b = relative(left).parts, relative(right).parts
    return a == b[:len(a)] or b == a[:len(b)]


def read_json(path):
    def unique(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    require(path.stat().st_size <= 2_000_000, 'record exceeds size limit')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def validate_shape(value, schema, depth=0, budget=None):
    """Small fail-closed subset for these two checked-in schemas; no external dependency."""
    budget = budget if budget is not None else [0]
    budget[0] += 1
    require(depth <= 64 and budget[0] <= 100000, 'schema validation limit exceeded')
    allowed = {'$schema', '$id', 'title', 'description', 'type', 'required', 'properties',
               'additionalProperties', 'items', 'minItems', 'uniqueItems', 'enum', 'const',
               'pattern', 'minimum', 'minLength', 'allOf', 'if', 'then', 'else'}
    require(isinstance(schema, dict) and set(schema) <= allowed, 'unsupported schema keyword')
    kind = schema.get('type')
    kinds = {'object': lambda: isinstance(value, dict), 'array': lambda: isinstance(value, list),
             'string': lambda: isinstance(value, str), 'integer': lambda: type(value) is int,
             'boolean': lambda: type(value) is bool}
    require(kind is None or kind in kinds and kinds[kind](), 'schema type mismatch')
    canonical = lambda x: json.dumps(x, sort_keys=True, allow_nan=False, separators=(',', ':'))
    if 'const' in schema:
        require(canonical(value) == canonical(schema['const']), 'schema constant mismatch')
    if 'enum' in schema:
        require(any(canonical(value) == canonical(x) for x in schema['enum']), 'schema enum mismatch')
    if isinstance(value, str):
        require(len(value) >= schema.get('minLength', 0), 'schema string too short')
        if 'pattern' in schema:
            require(re.search(schema['pattern'], value) is not None, 'schema pattern mismatch')
    if type(value) is int and 'minimum' in schema:
        require(value >= schema['minimum'], 'schema number below minimum')
    if isinstance(value, dict):
        require(set(schema.get('required', [])) <= set(value), 'schema required field missing')
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            require(set(value) <= set(properties), 'schema unknown field')
        for key, item in value.items():
            if key in properties:
                validate_shape(item, properties[key], depth + 1, budget)
    if isinstance(value, list):
        require(len(value) >= schema.get('minItems', 0), 'schema array too short')
        if schema.get('uniqueItems'):
            require(len(value) == len({canonical(x) for x in value}), 'schema duplicate array item')
        for item in value:
            validate_shape(item, schema.get('items', {}), depth + 1, budget)
    for branch in schema.get('allOf', []):
        validate_shape(value, branch, depth + 1, budget)
    if 'if' in schema:
        try:
            validate_shape(value, schema['if'], depth + 1, budget)
            matches = True
        except ValueError:
            matches = False
        branch = schema.get('then' if matches else 'else')
        if branch is not None:
            validate_shape(value, branch, depth + 1, budget)


def validate_format(record, name):
    schema_path = Path(__file__).resolve().parents[1] / 'schemas' / name
    validate_shape(record, read_json(schema_path))


def evidence(records, root):
    require(isinstance(records, list), 'evidence must be an array')
    seen = {}
    root = root.resolve()
    for item in records:
        require(isinstance(item, dict) and text(item.get('id')) and item['id'] not in seen, 'duplicate/missing evidence id')
        require(HEX40.fullmatch(str(item.get('candidate', ''))), 'evidence candidate missing')
        seen[item['id']] = item['candidate']
        p = root / relative(item.get('path'))
        require(HEX64.fullmatch(str(item.get('sha256', ''))), 'invalid evidence digest')
        current = root
        for part in relative(item['path']).parts:
            current /= part
            require(not current.is_symlink(), 'symlink evidence prohibited')
        require(p.is_file() and p.resolve().is_relative_to(root) and p.stat().st_size <= 10_000_000, 'unavailable evidence')
        require(hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], 'changed evidence bytes')
    return seen


def validate(record, root, expected_candidate, required_checks):
    validate_format(record, 'task-execution.schema.json')
    require(isinstance(record, dict) and type(record.get('schema_version')) is int and record.get('schema_version') == 1, 'unsupported task record')
    require(HEX40.fullmatch(expected_candidate) and record.get('candidate') == expected_candidate, 'candidate mismatch')
    require(bool(required_checks) and len(required_checks) == len(set(required_checks)), 'reviewed required checks must be nonempty/unique')
    ids = evidence(record.get('evidence'), root)
    tasks = record.get('tasks')
    require(isinstance(tasks, list) and tasks, 'missing task scope')
    index = {}
    for task in tasks:
        require(isinstance(task, dict) and text(task.get('id')) and task['id'] not in index, 'duplicate/missing task id')
        index[task['id']] = task
        require(text(task.get('owner')) and text(task.get('acceptance')), 'missing owner/acceptance')
        require(task.get('status') in {'TODO', 'READY', 'RUNNING', 'DONE', 'BLOCKED'}, 'invalid task status')
        paths = task.get('allowed_paths')
        require(isinstance(paths, list) and paths and len(paths) == len(set(paths)), 'missing/duplicate owned paths')
        for p in paths:
            relative(p)
        budget = task.get('budget')
        require(isinstance(budget, dict) and text(budget.get('unit')) and type(budget.get('limit')) is int and type(budget.get('spent')) is int and 0 <= budget['spent'] <= budget['limit'], 'invalid/exhausted task budget')
        deps = task.get('depends_on')
        require(isinstance(deps, list) and all(text(x) for x in deps) and len(set(deps)) == len(deps) and task['id'] not in deps, 'invalid dependencies')
        ready = task.get('ready_conditions')
        require(isinstance(ready, list) and ready and all(isinstance(x, dict) and text(x.get('condition')) and type(x.get('met')) is bool for x in ready), 'missing readiness conditions')
        resources = task.get('resources')
        require(isinstance(resources, list), 'missing resource inventory')
        resource_ids = set()
        for r in resources:
            require(isinstance(r, dict) and r.get('kind') in {'device', 'cache', 'output'} and text(r.get('key')) and r.get('mode') in {'read', 'exclusive'}, 'invalid resource claim')
            require((r['kind'], r['key']) not in resource_ids, 'duplicate resource claim')
            resource_ids.add((r['kind'], r['key']))
            if r['kind'] in {'cache', 'output'}:
                relative(r['key'])
        if task['status'] == 'DONE':
            result = task.get('result')
            require(isinstance(result, dict) and HEX40.fullmatch(str(result.get('candidate', ''))) and text(result.get('summary')), 'missing delegation result')
            changed = result.get('changed_paths')
            require(isinstance(changed, list) and all(any(overlaps(p, allowed) and relative(p).parts[:len(relative(allowed).parts)] == relative(allowed).parts for allowed in paths) for p in changed), 'result writes outside allowed paths')
            refs = result.get('evidence_ids')
            require(isinstance(refs, list) and refs and all(ids.get(x) == result['candidate'] for x in refs), 'result evidence missing/stale')
    visiting, done = set(), set()
    def visit(key):
        require(key in index, 'unknown task dependency')
        require(key not in visiting, 'cyclic dependencies')
        if key in done:
            return
        visiting.add(key)
        for dep in index[key]['depends_on']:
            visit(dep)
        visiting.remove(key)
        done.add(key)
    for key, task in index.items():
        visit(key)
        if task['status'] in {'READY', 'RUNNING', 'DONE'}:
            require(all(index[d]['status'] == 'DONE' for d in task['depends_on']), 'dependency not ready')
            require(all(c['met'] for c in task['ready_conditions']), 'readiness condition unmet')
    active = [t for t in tasks if t['status'] in {'READY', 'RUNNING'}]
    for i, a in enumerate(active):
        for b in active[i + 1:]:
            require(not any(overlaps(x, y) for x in a['allowed_paths'] for y in b['allowed_paths']), 'conflicting active write scope')
            for x in a['resources']:
                for y in b['resources']:
                    shared = (x['kind'] == y['kind'] == 'device' and x['key'] == y['key']) or (
                        x['kind'] in {'cache', 'output'} and y['kind'] in {'cache', 'output'} and overlaps(x['key'], y['key']))
                    require(not (shared and 'exclusive' in {x['mode'], y['mode']}), 'shared resource conflict')
    checks = record.get('integration_checks')
    require(isinstance(checks, list), 'missing integration checks')
    check_ids, outcomes = set(), []
    for check in checks:
        require(isinstance(check, dict) and text(check.get('id')) and check['id'] not in check_ids, 'duplicate/missing check id')
        check_ids.add(check['id'])
        require(check.get('candidate') == expected_candidate and check.get('status') in STATUSES, 'stale/invalid integration check')
        if check['status'] == 'PASS':
            require(isinstance(check.get('evidence_ids'), list) and check['evidence_ids'] and all(ids.get(x) == expected_candidate for x in check['evidence_ids']), 'PASS without current check evidence')
        else:
            require(text(check.get('reason')), 'non-PASS needs reason')
        if check['id'] in required_checks:
            outcomes.append(check['status'])
    require(set(required_checks) <= check_ids, 'missing reviewed integration check')
    review = record.get('review')
    require(isinstance(review, dict) and review.get('candidate') == expected_candidate and text(review.get('reviewer')), 'missing/stale review')
    for role in ('spec', 'quality'):
        conclusion = review.get(role)
        require(isinstance(conclusion, dict) and conclusion.get('status') in STATUSES and text(conclusion.get('basis')), 'missing spec/quality conclusion')
        outcomes.append(conclusion['status'])
    findings = review.get('findings')
    require(isinstance(findings, list), 'missing review findings')
    for finding in findings:
        require(isinstance(finding, dict) and text(finding.get('location')) and text(finding.get('consequence')) and text(finding.get('basis')) and type(finding.get('blocking')) is bool and type(finding.get('resolved')) is bool, 'incomplete review finding')
        if finding['blocking']:
            if not finding['resolved']:
                outcomes.append('FAIL')
            else:
                refs = finding.get('resolution_evidence_ids')
                require(isinstance(refs, list) and refs and all(ids.get(x) == expected_candidate for x in refs), 'blocking finding resolved without current Evidence')
    state = 'FAIL' if 'FAIL' in outcomes else 'BLOCKED' if any(x != 'PASS' for x in outcomes) or any(t['status'] != 'DONE' for t in tasks) else 'PASS'
    return {'status': state, 'scope': 'task-record-consistency', 'candidate': expected_candidate,
            'host_certified': False, 'execution_certified': False, 'task_count': len(tasks)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record', type=Path, required=True)
    p.add_argument('--evidence-root', type=Path, required=True)
    p.add_argument('--expected-candidate', required=True)
    p.add_argument('--required-check', action='append', required=True)
    args = p.parse_args()
    try:
        report = validate(read_json(args.record), args.evidence_root, args.expected_candidate, args.required_check)
        print(json.dumps(report))
        return 0 if report['status'] == 'PASS' else 1
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({'status': 'FAIL', 'scope': 'task-record-consistency', 'error': str(exc), 'host_certified': False}))
        return 1

if __name__ == '__main__':
    sys.exit(main())
