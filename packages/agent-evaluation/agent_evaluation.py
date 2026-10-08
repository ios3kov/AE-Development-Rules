#!/usr/bin/env python3
"""Observer-owned action adapter for existing AI fixtures; no model or host certification."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import statistics
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone

# Shared standard helpers remain in the adopted checkout; no external installs.
_STANDARD_SCRIPTS = Path(__file__).resolve().parents[2] / 'starter-kit/scripts'
sys.path.insert(0, str(_STANDARD_SCRIPTS))

from check_reference_obligations import load_json, canonical, HEX, REV, timestamp
import agent_skills

PARTITIONS = {'tune', 'select', 'final'}
MAX_BYTES = 1024 * 1024


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(root, name, must_exist=False):
    require(isinstance(name, str) and name and '\\' not in name and ':' not in name, 'invalid relative path')
    require(not name.startswith('/') and all(p not in {'', '.', '..', '.git'} for p in name.split('/')), 'unsafe relative path')
    base = Path(root).resolve(strict=True)
    result = base / name
    cursor = base
    for part in name.split('/'):
        cursor /= part
        require(not cursor.is_symlink(), 'symlink path forbidden')
    require(result.resolve().is_relative_to(base), 'path escape')
    if must_exist:
        require(result.is_file(), 'file missing')
    return result


def snapshot(root):
    result = {}
    for path in sorted(Path(root).rglob('*')):
        require(not path.is_symlink(), 'symlink snapshot rejected')
        name = path.relative_to(root).as_posix()
        if path.is_file():
            require(path.stat().st_size <= MAX_BYTES, 'oversized fixture')
            result[name] = {'sha256': digest(path.read_bytes()), 'mode': path.stat().st_mode & 0o7777}
        else:
            require(path.is_dir(), 'unsupported filesystem entry')
    return result


def case_errors(case):
    errors = []
    if not isinstance(case, dict):
        return ['case object required']
    if set(case) - {'id','partition','request','context','should_select_skill','files','edit_paths','checks','objectives','observer_files'}:
        errors.append('unsupported case fields')
    if 'context' in case and (not isinstance(case['context'], list) or any(not isinstance(x, str) for x in case['context'])):
        errors.append('invalid case context')
    for key in ['id', 'request']:
        if not isinstance(case.get(key), str) or not case[key].strip():
            errors.append('case ' + key + ' required')
    if case.get('partition') not in PARTITIONS:
        errors.append('tune/select/final partition required')
    if type(case.get('should_select_skill')) is not bool:
        errors.append('skill selection criterion required')
    files = case.get('files')
    if not isinstance(files, dict) or not files:
        errors.append('fixture files required')
    else:
        for name, value in files.items():
            if not isinstance(name, str) or name.startswith('/') or '\\' in name or ':' in name or any(p in {'', '.', '..', '.git'} for p in name.split('/')) or not isinstance(value, str):
                errors.append('unsafe fixture file')
    observer = case.get('observer_files')
    if not isinstance(observer,dict) or any(not isinstance(name,str) or name.startswith('/') or '\\' in name or ':' in name or any(p in {'','.','..','.git'} for p in name.split('/')) or not isinstance(content,str) for name,content in (observer.items() if isinstance(observer,dict) else [])):
        errors.append('safe observer checker files required')
    allowed = case.get('edit_paths')
    if not isinstance(allowed, list) or any(not isinstance(x,str) for x in allowed) or len(set(allowed)) != len(allowed) or any(p not in (files or {}) for p in allowed):
        errors.append('explicit existing edit paths required')
    if not isinstance(case.get('checks'), dict):
        errors.append('check alias map required')
    else:
        for alias, argv in case['checks'].items():
            if not isinstance(alias, str) or not re.fullmatch('[A-Za-z0-9_-]+', alias) or not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x for x in argv):
                errors.append('invalid controlled command')
    objectives = case.get('objectives')
    if not isinstance(objectives, list) or not objectives:
        errors.append('objective checks required')
    else:
        seen = set()
        for item in objectives:
            if not isinstance(item, dict) or not isinstance(item.get('id'), str) or item['id'] in seen or type(item.get('critical')) is not bool:
                errors.append('unique objective ID and critical flag required')
                continue
            seen.add(item['id'])
            if set(item) - {'id','critical','kind','arm','path','keys','value','alias','key','op','min','max'}:
                errors.append('unsupported objective fields')
            if item.get('kind') not in {'file_equals', 'json_equals', 'command_pass', 'action_count', 'final_claim'}:
                errors.append('unknown objective kind')
            if item.get('kind') in {'file_equals', 'json_equals'} and item.get('path') not in (files or {}):
                errors.append('objective file absent')
            if item.get('kind') == 'command_pass' and item.get('alias') not in case.get('checks', {}):
                errors.append('objective check alias absent')
            if item.get('arm') not in {None, 'baseline', 'selected_skill'}:
                errors.append('invalid objective arm')
            if item.get('kind') == 'final_claim' and not isinstance(item.get('key'), str):
                errors.append('final typed claim key required')
            if item.get('kind') == 'action_count' and (item.get('op') not in {'read', 'write', 'check', 'select_skill', 'read_skill_resource', 'finish'} or type(item.get('min')) is not int or type(item.get('max')) is not int or item['min'] < 0 or item['max'] < item['min']):
                errors.append('invalid action count bounds')
    return errors


def validate_plan(plan, catalog):
    require(isinstance(plan, dict) and type(plan.get('schema_version')) is int and plan['schema_version'] == 1, 'evaluation plan v1 required')
    allowed = {'schema_version','partition','standard_commit','standard_snapshot_sha256','catalog_sha256','agent_configuration_sha256','model','mode','case_ids','selected_skill','repetitions','max_actions','timeout_s','repair_budget','no_progress_limit','selected_configuration_sha256','oracle_exposed_to_configuration'}
    require(not set(plan) - allowed, 'unsupported protected plan fields')
    require(plan.get('partition') in PARTITIONS, 'partition required')
    require(isinstance(plan.get('standard_commit'), str) and REV.fullmatch(plan['standard_commit']), 'exact standard SHA required')
    for field in ['catalog_sha256', 'agent_configuration_sha256', 'standard_snapshot_sha256']:
        require(isinstance(plan.get(field), str) and HEX.fullmatch(plan[field]), 'invalid ' + field)
    require(digest(catalog) == plan['catalog_sha256'], 'catalog changed')
    require(isinstance(catalog, dict) and not set(catalog) - {'schema_version','description','cases'} and type(catalog.get('schema_version')) is int and catalog['schema_version'] == 1 and isinstance(catalog.get('cases'), list), 'evaluation fixture catalog v1 required')
    ids = [c.get('id') for c in catalog['cases'] if isinstance(c, dict)]
    require(len(ids) == len(catalog['cases']) and len(ids) == len(set(ids)), 'duplicate or invalid case')
    for case in catalog['cases']:
        require(not case_errors(case), '; '.join(case_errors(case)))
    selected = plan.get('case_ids')
    require(isinstance(selected, list) and selected and all(isinstance(x,str) for x in selected) and len(selected) == len(set(selected)) and all(x in ids for x in selected), 'unique known selected cases required')
    cases = [c for c in catalog['cases'] if c['id'] in selected]
    require(all(c['partition'] == plan['partition'] for c in cases), 'partition mixing forbidden')
    if plan['partition'] == 'final':
        require(plan.get('selected_configuration_sha256') == plan['agent_configuration_sha256'], 'final configuration must be frozen after selection')
        require(plan.get('oracle_exposed_to_configuration') is False, 'contaminated final evaluation blocked')
    for field, maximum in [('repetitions', 20), ('max_actions', 200), ('repair_budget', 10), ('no_progress_limit', 10), ('timeout_s', 600)]:
        require(type(plan.get(field)) is int and 1 <= plan[field] <= maximum, 'invalid bounded ' + field)
    skill = plan.get('selected_skill')
    require(isinstance(skill, dict) and set(skill) == {'name','source_commit','package_sha256','policy_sha256','task','available_tools'} and isinstance(skill.get('name'), str) and skill['name'], 'protected selected skill identity required')
    for field in ['package_sha256', 'policy_sha256']:
        require(isinstance(skill.get(field), str) and HEX.fullmatch(skill[field]), 'sealed full package/policy required')
    require(isinstance(skill.get('source_commit'), str) and REV.fullmatch(skill['source_commit']), 'exact selected skill source revision required')
    require(isinstance(skill.get('task'), str) and skill['task'] and isinstance(skill.get('available_tools'), list) and all(isinstance(x, str) and x for x in skill['available_tools']) and len(set(skill['available_tools'])) == len(skill['available_tools']), 'explicit task/tool inventory required')
    require(isinstance(plan.get('model'), str) and plan['model'], 'model identity required')
    require(plan.get('mode') in {'LIVE', 'SYNTHETIC'}, 'explicit live/synthetic mode required')
    return cases


class IsolationUnavailable(RuntimeError):
    pass


class Isolation:
    """No network, read-only inputs; project changes happen only through the observer broker."""
    def __init__(self, visible, runtime_roots, private):
        self.visible = [Path(p).resolve(strict=True) for p in visible]
        self.private = [Path(p).resolve(strict=True) for p in (private if isinstance(private, list) else [private])]
        self.observer = next((p for p in self.private if p.is_dir()), None)
        require(self.observer is not None, 'observer storage required')
        self.runtime = [Path(p).resolve(strict=True) for p in runtime_roots]
        system = [Path(p).resolve() for p in ['/usr', '/bin', '/System', '/Library', '/private/etc'] if Path(p).exists()]
        for p in self.visible + self.runtime + system:
            require(all(not private.is_relative_to(p) and not p.is_relative_to(private) for private in self.private), 'isolation root overlaps observer data')
        if sys.platform == 'darwin' and shutil.which('sandbox-exec'):
            self.backend = 'sandbox-exec'
        elif sys.platform.startswith('linux') and shutil.which('bwrap'):
            self.backend = 'bwrap'
        else:
            raise IsolationUnavailable('supported OS isolation unavailable; agent execution BLOCKED')

    def wrap(self, argv, cwd):
        require(isinstance(argv, list) and argv and all(isinstance(v, str) and v for v in argv), 'explicit executable argv required')
        executable = shutil.which(argv[0]) if not Path(argv[0]).is_absolute() else argv[0]
        if not executable or not Path(executable).is_file():
            raise IsolationUnavailable('agent/check executable unavailable')
        argv = [str(Path(executable).resolve()), *argv[1:]]
        roots = self.visible + self.runtime
        if self.backend == 'sandbox-exec':
            # Escape through JSON strings, which match SBPL quoted strings for paths.
            paths = ' '.join('(subpath ' + json.dumps(str(p)) + ')' for p in roots)
            system = ['/usr', '/bin', '/System', '/Library', '/private/etc', '/dev/null', '/dev/urandom', '/dev/random']
            reads = paths + ' ' + ' '.join('(subpath ' + json.dumps(p) + ')' for p in system)
            policy = '(version 1)(deny default)(allow process-exec)(allow signal (target self))(allow sysctl-read)(allow file-read* ' + reads + ')(allow file-write-data (literal "/dev/null"))'
            return ['sandbox-exec', '-p', policy, *argv]
        command = ['bwrap', '--die-with-parent', '--new-session', '--unshare-all', '--cap-drop', 'ALL', '--proc', '/proc', '--dev', '/dev']
        for p in ['/usr', '/bin', '/lib', '/lib64', '/etc/ld.so.cache']:
            if Path(p).exists():
                command += ['--ro-bind', str(Path(p).resolve()), p]
        for p in roots:
            command += ['--ro-bind', str(p), str(p)]
        return command + ['--chdir', str(cwd), '--', *argv]

    def probe(self, executable, cwd):
        # Check actual denied reads/writes, not presence of a launcher binary.
        canary = self.observer / 'isolation-canary'
        canary.write_text('observer-only')
        exposed = Path(cwd) / 'probe-read-only'
        exposed.write_text('immutable')
        code = 'import pathlib,sys; q=pathlib.Path(sys.argv[1]);\nfor name in sys.argv[2:]:\n p=pathlib.Path(name)\n try:\n  list(p.iterdir()) if p.is_dir() else p.read_bytes(); sys.exit(31)\n except (PermissionError,FileNotFoundError):pass\ntry:q.write_text("changed");sys.exit(32)\nexcept PermissionError:pass\nexcept OSError:pass\nprint("ISOLATION_PASS")'
        try:
            r = subprocess.run(self.wrap([str(executable), '-c', code, str(exposed), str(canary), *map(str, self.private)], cwd), cwd=cwd,
                               capture_output=True, timeout=10, env=clean_environment(), text=True)
            if r.returncode or r.stdout.strip() != 'ISOLATION_PASS' or exposed.read_text() != 'immutable':
                raise IsolationUnavailable('isolation enforcement probe failed; execution BLOCKED')
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise IsolationUnavailable('isolation probe unavailable; execution BLOCKED') from exc
        finally:
            canary.unlink(missing_ok=True)
            exposed.unlink(missing_ok=True)


def clean_environment():
    # Credentials, HOME, model caches and agent hooks are never inherited.
    return {'PATH': '/usr/bin:/bin:/usr/local/bin', 'LANG': 'en_US.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1', 'HOME': '/nonexistent', 'TMPDIR': '/nonexistent'}


def stop_process(proc, grace=1):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        pass
    # The parent may exit before a descendant that retains a pipe. Reap the
    # owned group even in that case before evaluating observer objectives.
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait(timeout=2)


def controlled_check(alias, case, project, isolation, timeout=15, checker_root=None):
    argv = case['checks'][alias]
    try:
        argv = [str(safe_path(checker_root, arg[len('@observer/'):],True)) if arg.startswith('@observer/') and checker_root is not None else arg for arg in argv]
        require(not any(arg.startswith('@observer/') for arg in argv), 'observer checker root unavailable')
    except (ValueError,OSError):
        return {'alias':alias,'exit_code':None,'duration_ms':0.0,'status':'BLOCKED','reason':'observer checker unavailable'}
    begin = time.monotonic()
    if os.name == 'nt':
        return {'alias': alias, 'exit_code': None, 'duration_ms': 0.0, 'status': 'BLOCKED', 'reason': 'process monitoring/isolation unavailable on Windows'}
    outputs = {'stdout': bytearray(), 'stderr': bytearray()}
    proc = None; selector = selectors.DefaultSelector(); blocked = None
    try:
        proc = subprocess.Popen(isolation.wrap(argv, project), cwd=project, env=clean_environment(), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, start_new_session=True)
        selector.register(proc.stdout, selectors.EVENT_READ, 'stdout'); selector.register(proc.stderr, selectors.EVENT_READ, 'stderr')
        while selector.get_map():
            if time.monotonic() - begin >= timeout:
                blocked = 'command timeout'; break
            for key, _ in selector.select(min(.1, max(0, timeout - (time.monotonic() - begin)))):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj); continue
                outputs[key.data].extend(chunk)
                if sum(map(len, outputs.values())) > MAX_BYTES:
                    blocked = 'command output budget'; break
            if blocked:
                break
        if not blocked:
            try:
                proc.wait(timeout=max(.01, timeout - (time.monotonic() - begin)))
            except subprocess.TimeoutExpired:
                blocked = 'command timeout'
    except (OSError, ValueError, IsolationUnavailable):
        blocked = 'command unavailable'
    finally:
        selector.close()
        if proc:
            stop_process(proc, grace=.1)
            proc.stdout.close(); proc.stderr.close()
    stdout = bytes(outputs['stdout']); stderr = bytes(outputs['stderr'])
    code = proc.returncode if proc else None
    return {'alias': alias, 'exit_code': code, 'duration_ms': round((time.monotonic() - begin) * 1000, 3),
            'stdout_sha256': digest(stdout), 'stderr_sha256': digest(stderr), 'output': stdout[:4096].decode('utf-8', 'replace'),
            'status': 'BLOCKED' if blocked else ('PASS' if code == 0 else 'FAIL'), 'reason': blocked}


class Broker:
    def __init__(self, case, project, isolation, skill_text=None, plan=None, skill_loader=None, checker_root=None, checker_isolation=None):
        self.case, self.project, self.isolation, self.skill_text = case, Path(project), isolation, skill_text
        self.plan = plan or {'repair_budget': 3, 'no_progress_limit': 2}
        self.skill_loader, self.skill_selected = skill_loader, False
        self.checker_root, self.checker_isolation = checker_root, checker_isolation or isolation
        self.receipts, self.violations, self.checks = [], [], []
        self.finished, self.repair_count = False, 0
        self.check_progress = {}

    def handle(self, request, check_timeout=15):
        require(isinstance(request, dict) and isinstance(request.get('op'), str), 'invalid agent protocol')
        begin = time.monotonic()
        receipt = {'sequence': len(self.receipts) + 1, 'request': request, 'started_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}
        op = request['op']
        try:
            if op == 'read':
                p = safe_path(self.project, request.get('path'), True)
                require(p.stat().st_size <= MAX_BYTES, 'oversized read')
                result = {'status': 'PASS', 'content': p.read_text(), 'sha256': digest(p.read_bytes())}
            elif op == 'write':
                require(request.get('path') in self.case['edit_paths'], 'forbidden write')
                require(isinstance(request.get('content'), str) and len(request['content'].encode()) <= MAX_BYTES, 'invalid write content')
                p = safe_path(self.project, request['path'], True)
                p.write_text(request['content'])
                result = {'status': 'PASS', 'sha256': digest(p.read_bytes())}
            elif op == 'check':
                require(request.get('alias') in self.case['checks'], 'command alias forbidden')
                alias = request['alias']
                current = digest(snapshot(self.project))
                previous = self.check_progress.get(alias)
                # First executions of distinct checks are validation, not repair attempts.
                if previous is not None:
                    self.repair_count += 1
                require(self.repair_count <= self.plan['repair_budget'], 'repair budget exhausted')
                result = controlled_check(alias, self.case, self.project, self.checker_isolation,
                                          timeout=check_timeout, checker_root=self.checker_root)
                self.checks.append(result)
                # Observe the result before deciding: the same files can produce new evidence.
                outcome = digest({key: result.get(key) for key in
                                  ('status', 'exit_code', 'stdout_sha256', 'stderr_sha256', 'reason')})
                signature = (current, outcome)
                stalls = previous[1] + 1 if previous and previous[0] == signature else 0
                self.check_progress[alias] = (signature, stalls)
                require(stalls < self.plan['no_progress_limit'], 'no-progress budget exhausted')
            elif op == 'select_skill':
                if self.skill_text is None:
                    result = {'status': 'BLOCKED', 'reason': 'baseline arm has no selected skill'}
                else:
                    require(self.case['should_select_skill'], 'irrelevant/unauthorized skill selection')
                    result = self.skill_loader('SKILL.md') if self.skill_loader else {'status': 'PASS', 'content': self.skill_text, 'sha256': digest(self.skill_text.encode())}
                    self.skill_selected = True
            elif op == 'read_skill_resource':
                require(self.skill_selected and self.skill_loader is not None, 'skill resource requires prior approved selection')
                result = self.skill_loader(request.get('path'))
            elif op == 'finish':
                require(isinstance(request.get('message'), str) and isinstance(request.get('claims'), dict), 'final message and typed factual claims required')
                self.finished = True
                result = {'status': 'PASS', 'recorded': True}
            else:
                raise ValueError('forbidden operation: ' + op)
        except (ValueError, OSError, UnicodeError) as exc:
            self.violations.append(str(exc))
            result = {'status': 'FAIL', 'reason': str(exc)}
        receipt['result'] = result
        receipt['duration_ms'] = round((time.monotonic() - begin) * 1000, 3)
        self.receipts.append(receipt)
        return result


def objective_results(case, project, broker, arm=None):
    results = []
    for check in case['objectives']:
        if check.get('arm') is not None and check['arm'] != arm:
            continue
        try:
            if check['kind'] == 'file_equals':
                ok = safe_path(project, check['path'], True).read_text() == check['value']
            elif check['kind'] == 'json_equals':
                data = load_json(safe_path(project, check['path'], True))
                value = data
                for key in check.get('keys', []):
                    value = value[key]
                ok = value == check['value']
            elif check['kind'] == 'final_claim':
                finished = [r['request'] for r in broker.receipts if r['request']['op'] == 'finish']
                ok = len(finished) == 1 and finished[0]['claims'].get(check['key']) == check['value']
            elif check['kind'] == 'command_pass':
                actual = controlled_check(check['alias'], case, project, broker.checker_isolation, checker_root=broker.checker_root)
                ok = actual['status'] == 'PASS'
                results.append({'id': check['id'], 'critical': check['critical'], 'status': 'PASS' if ok else actual['status'], 'receipt': actual})
                continue
            else:
                count = sum(r['request']['op'] == check['op'] and r['result']['status'] == 'PASS' for r in broker.receipts)
                ok = check['min'] <= count <= check['max']
            results.append({'id': check['id'], 'critical': check['critical'], 'status': 'PASS' if ok else 'FAIL'})
        except (ValueError, OSError, KeyError, TypeError, UnicodeError):
            results.append({'id': check['id'], 'critical': check['critical'], 'status': 'FAIL'})
    return results


def usage_receipt(path, run_id, configuration):
    if path is None:
        return {'status': 'NOT_RUN', 'tokens': None, 'cost': None, 'reason': 'provider usage receipt unavailable'}
    data = load_json(path)
    require(data.get('run_id') == run_id and data.get('configuration_sha256') == configuration, 'usage receipt identity mismatch')
    require(data.get('authority') == 'provider' and isinstance(data.get('request_ids'), list) and data['request_ids'] and len(set(data['request_ids'])) == len(data['request_ids']), 'provider request receipt required')
    for field in ['tokens', 'cost']:
        value = data.get(field)
        require(type(value) in {int, float} and math.isfinite(value) and value >= 0, 'invalid measured ' + field)
    require(isinstance(data.get('currency'), str) and data['currency'], 'usage currency required')
    return {'status': 'PASS', 'tokens': data['tokens'], 'cost': data['cost'], 'currency': data['currency'], 'receipt_sha256': digest(Path(path).read_bytes()), 'request_ids': data['request_ids']}


def launch_agent(argv, broker, visible, plan, run_id, arm=None):
    before = snapshot(broker.project)
    started = time.monotonic()
    proc = subprocess.Popen(broker.isolation.wrap(argv, visible), cwd=visible, env=clean_environment(),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            start_new_session=True, bufsize=0)
    public = {'protocol_version': 1, 'run_id': run_id, 'request': broker.case['request'], 'context': broker.case.get('context', []),
              'files': list(broker.case['files']), 'edit_paths': broker.case['edit_paths'], 'check_aliases': list(broker.case['checks']),
              'selected_skill_available': broker.skill_text is not None,
              'final_claim_fields': ['runtime_status'],
              'operations': ['read', 'write', 'check', 'select_skill', 'read_skill_resource', 'finish'], 'standard': 'standard/AI_ENTRYPOINT.md',
              'instruction': 'Use JSON lines requests on stdout; receive observer-executed responses on stdin. Direct writes/network/accounts/host operations are unavailable.'}
    selector = selectors.DefaultSelector()
    deadline = started + plan['timeout_s']
    pending = b''
    outgoing = canonical(public) + b'\n'
    sent = 0
    try:
        os.set_blocking(proc.stdin.fileno(), False)
        os.set_blocking(proc.stdout.fileno(), False)
        selector.register(proc.stdin, selectors.EVENT_WRITE)
        selector.register(proc.stdout, selectors.EVENT_READ)
        while not broker.violations and (not broker.finished or outgoing):
            require(time.monotonic() < deadline, 'agent timeout')
            # Dispatch one buffered request only after the preceding response
            # has been sent. Both pipe directions share the same deadline.
            if b'\n' in pending and not outgoing and not broker.finished:
                line, pending = pending.split(b'\n', 1)
                require(len(broker.receipts) < plan['max_actions'], 'action budget exhausted')
                # Strict JSON prevents ambiguous receipt fields/NaN.
                def pairs(items):
                    value = {}
                    for k, v in items:
                        require(k not in value, 'duplicate protocol key')
                        value[k] = v
                    return value
                request = json.loads(line, object_pairs_hook=pairs, parse_constant=lambda v: (_ for _ in ()).throw(ValueError('nonfinite protocol')))
                response = broker.handle(request, check_timeout=min(15, max(0, deadline - time.monotonic())))
                require(time.monotonic() < deadline, 'agent timeout')
                outgoing, sent = canonical(response) + b'\n', 0
                selector.register(proc.stdin, selectors.EVENT_WRITE)
            if not selector.get_map():
                break
            for key, _ in selector.select(min(.2, max(0, deadline - time.monotonic()))):
                if key.fileobj is proc.stdin:
                    try:
                        count = os.write(proc.stdin.fileno(), memoryview(outgoing)[sent:sent + 65536])
                    except BlockingIOError:
                        continue
                    sent += count
                    if sent == len(outgoing):
                        outgoing, sent = b'', 0
                        selector.unregister(proc.stdin)
                else:
                    try:
                        chunk = os.read(proc.stdout.fileno(), 65536)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(proc.stdout)
                        continue
                    pending += chunk
                    require(len(pending) <= MAX_BYTES, 'oversized protocol output')
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        broker.violations.append(str(exc))
    finally:
        selector.close()
        # Reap the entire owned process group before checking hidden objectives.
        stop_process(proc, grace=.1)
        proc.stdin.close(); proc.stdout.close()
    after = snapshot(broker.project)
    unauthorized = [p for p in set(before) | set(after) if before.get(p) != after.get(p) and p not in broker.case['edit_paths']]
    if unauthorized:
        broker.violations.append('unauthorized file changes')
    objectives = objective_results(broker.case, broker.project, broker, arm)
    passed = broker.finished and not broker.violations and all(c['status'] == 'PASS' for c in objectives)
    return {'run_id': run_id, 'status': ('PASS' if plan['mode'] == 'LIVE' else 'SYNTHETIC_PASS') if passed else 'FAIL',
            'mode': plan['mode'], 'scope': 'acting-agent-objective-fixture' if plan['mode'] == 'LIVE' else 'adapter-contract-only',
            'duration_ms': round((time.monotonic() - started) * 1000, 3), 'critical_violation': bool(broker.violations) or any(c['critical'] and c['status'] != 'PASS' for c in objectives),
            'violations': broker.violations, 'objectives': objectives, 'action_receipts': broker.receipts, 'final_files': after,
            'observed_action_scope': 'broker-requests/results and final project files; direct denied OS syscalls are not individually audited',
            'agent_effectiveness_certified': False, 'ae_host_certified': False}


def validate_run(run):
    require(isinstance(run, dict), 'run object required')
    require(run.get('mode') in {'LIVE','SYNTHETIC'}, 'run execution mode required')
    for field in ['agent_configuration_sha256','standard_snapshot_sha256','catalog_sha256']:
        require(isinstance(run.get(field),str) and HEX.fullmatch(run[field]), 'invalid experiment '+field)
    require(isinstance(run.get('standard_commit'),str) and REV.fullmatch(run['standard_commit']), 'exact observed standard SHA required')
    if run.get('status') in {'BLOCKED', 'NOT_RUN'}:
        require(run.get('critical_violation') is False and run.get('duration_ms') is None, 'unexecuted run cannot have measured success')
        usage=run.get('usage')
        require(isinstance(usage,dict) and usage.get('status') == 'NOT_RUN' and usage.get('tokens') is None and usage.get('cost') is None, 'unexecuted run cannot have measured provider usage')
        return
    expected_scope='acting-agent-objective-fixture' if run['mode']=='LIVE' else 'adapter-contract-only'
    require(run.get('scope') == expected_scope, 'mode/scope contradiction')
    require(run.get('mode') != 'LIVE' or run.get('status') != 'SYNTHETIC_PASS', 'synthetic status cannot become live execution')
    require(run.get('mode') != 'SYNTHETIC' or run.get('status') != 'PASS', 'synthetic run cannot become agent PASS')
    receipts, objectives = run.get('action_receipts'), run.get('objectives')
    require(isinstance(receipts, list) and isinstance(objectives, list) and objectives, 'actual actions and objective observations required')
    for number, receipt in enumerate(receipts, 1):
        require(isinstance(receipt, dict) and type(receipt.get('sequence')) is int and receipt['sequence'] == number, 'action sequence mismatch')
        require(isinstance(receipt.get('request'), dict) and isinstance(receipt['request'].get('op'), str), 'actual action request required')
        require(timestamp(receipt.get('started_at')) is not None, 'actual UTC action time required')
        require(isinstance(receipt.get('result'), dict) and receipt['result'].get('status') in {'PASS', 'FAIL', 'BLOCKED'}, 'actual action result required')
        require(type(receipt.get('duration_ms')) in {int, float} and math.isfinite(receipt['duration_ms']) and receipt['duration_ms'] >= 0, 'actual action duration required')
    require(len({x.get('id') for x in objectives}) == len(objectives), 'duplicate objective observation')
    for check in objectives:
        require(type(check.get('critical')) is bool and check.get('status') in {'PASS', 'FAIL', 'BLOCKED'}, 'objective verdict required')
        if 'receipt' in check:
            require(isinstance(check['receipt'], dict) and check['receipt'].get('status') == check['status'], 'objective receipt mismatch')
            if check['status'] == 'PASS':
                require(check['receipt'].get('exit_code') == 0, 'command PASS requires actual zero exit')
    require(isinstance(run.get('violations'), list), 'observed violation list required')
    expected_critical = bool(run['violations']) or any(x['critical'] and x['status'] != 'PASS' for x in objectives)
    require(run.get('critical_violation') == expected_critical, 'critical verdict suppressed')
    if run.get('status') in {'PASS', 'SYNTHETIC_PASS'}:
        require(not expected_critical and all(x['status'] == 'PASS' for x in objectives), 'failed objective cannot become PASS')
        require(sum(x['request']['op'] == 'finish' and x['result']['status'] == 'PASS' for x in receipts) == 1, 'actual final action required')
    usage = run.get('usage')
    require(isinstance(usage, dict) and usage.get('status') in {'PASS', 'NOT_RUN'}, 'usage measurement state required')
    if usage['status'] == 'PASS':
        require(isinstance(usage.get('receipt_sha256'), str) and HEX.fullmatch(usage['receipt_sha256']), 'usage source digest required')
        require(isinstance(usage.get('request_ids'), list) and usage['request_ids'] and len(set(usage['request_ids'])) == len(usage['request_ids']), 'unique provider requests required')
        for field in ['tokens', 'cost']:
            require(type(usage.get(field)) in {int, float} and math.isfinite(usage[field]) and usage[field] >= 0, 'invalid measured usage')
        require(isinstance(usage.get('currency'), str) and usage['currency'], 'usage currency required')
    else:
        require(usage.get('tokens') is None and usage.get('cost') is None, 'unknown usage is not zero cost')


def compare_runs(runs):
    require(isinstance(runs, list) and runs, 'actual run records required')
    seen = set(); requests = set()
    pairs = {}
    for run in runs:
        validate_run(run)
        require(isinstance(run, dict) and isinstance(run.get('run_id'), str) and run['run_id'] not in seen, 'unique run receipts required')
        seen.add(run['run_id'])
        require(isinstance(run.get('case_id'),str) and run['case_id'] and type(run.get('repetition')) is int and run['repetition'] >= 0, 'case/repetition identity required')
        require(run.get('arm') in {'baseline', 'selected_skill'} and run.get('partition') in PARTITIONS, 'comparison arm/partition required')
        require(run.get('mode') in {'LIVE', 'SYNTHETIC'} and run.get('status') in {'PASS', 'SYNTHETIC_PASS', 'FAIL', 'BLOCKED', 'NOT_RUN'}, 'explicit run status required')
        require(run.get('mode') != 'SYNTHETIC' or run.get('status') != 'PASS', 'synthetic PASS cannot become agent PASS')
        require((run.get('status') in {'BLOCKED', 'NOT_RUN'} and run.get('duration_ms') is None) or (type(run.get('duration_ms')) in {int, float} and math.isfinite(run['duration_ms']) and run['duration_ms'] >= 0), 'actual measured duration required')
        require(type(run.get('critical_violation')) is bool, 'critical verdict required')
        require(not (run['critical_violation'] and run['status'] in {'PASS', 'SYNTHETIC_PASS'}), 'critical violation cannot average into PASS')
        key = (run['case_id'], run['repetition'])
        require(run['arm'] not in pairs.setdefault(key, {}), 'duplicate comparison arm')
        pairs[key][run['arm']] = run
        for request in run.get('usage', {}).get('request_ids', []):
            require(request not in requests, 'provider usage replay')
            requests.add(request)
    require(len({r['mode'] for r in runs}) == 1, 'live/synthetic comparison mixing forbidden')
    selected_shas = {r.get('selected_skill_sha256') for r in runs if r['arm'] == 'selected_skill'}
    require(len(selected_shas) == 1 and all(isinstance(s, str) and HEX.fullmatch(s) for s in selected_shas), 'mixed/stale selected package identity')
    require(all(r.get('selected_skill_sha256') is None for r in runs if r['arm'] == 'baseline'), 'baseline contaminated by selected skill')
    require(len({r['standard_commit'] for r in runs}) == 1, 'mixed standard revisions')
    require(len({r['partition'] for r in runs}) == 1 and len({r['agent_configuration_sha256'] for r in runs}) == 1 and len({r['standard_snapshot_sha256'] for r in runs}) == 1 and len({r['catalog_sha256'] for r in runs}) == 1, 'mixed experiment identity')
    require(all(set(p) == {'baseline', 'selected_skill'} for p in pairs.values()), 'paired fresh arms required')
    arms = {}
    for arm in ['baseline', 'selected_skill']:
        subset = [r for r in runs if r['arm'] == arm]
        times = [r['duration_ms'] for r in subset if r['duration_ms'] is not None]
        measured = [r['usage'] for r in subset if r.get('usage', {}).get('status') == 'PASS']
        arms[arm] = {'runs': len(subset), 'objective_passes': sum(r['status'] in {'PASS', 'SYNTHETIC_PASS'} for r in subset),
                     'critical_violations': sum(r['critical_violation'] for r in subset), 'mean_duration_ms': statistics.mean(times) if times else None,
                     'duration_stddev_ms': statistics.pstdev(times) if times else None, 'usage_status': 'PASS' if len(measured) == len(subset) else 'NOT_RUN',
                     'total_tokens': sum(m['tokens'] for m in measured) if len(measured) == len(subset) else None,
                     'total_cost': sum(m['cost'] for m in measured) if len(measured) == len(subset) and len({m['currency'] for m in measured}) == 1 else None}
    live = all(r['mode'] == 'LIVE' for r in runs)
    unavailable = any(r['status'] in {'BLOCKED', 'NOT_RUN'} for r in runs)
    return {'schema_version': 1, 'status': 'BLOCKED' if unavailable else ('FAIL' if any(r['critical_violation'] or r['status'] == 'FAIL' for r in runs) else ('PASS' if live else 'SYNTHETIC_PASS')),
            'scope': 'paired-fixture-observations' if live else 'synthetic-adapter-contract-only', 'arms': arms,
            'live_agent_status': 'RUN' if live and any(r['status'] not in {'BLOCKED','NOT_RUN'} for r in runs) else 'NOT_RUN', 'effectiveness_claim': 'Requires independent reviewer of observed criteria, configured scope and repeated matched trials.', 'repeatability': [{'case_id': case, 'arm': arm, 'outcomes': [r['status'] for r in runs if r['case_id'] == case and r['arm'] == arm], 'consistent': len({r['status'] for r in runs if r['case_id'] == case and r['arm'] == arm}) == 1} for case in sorted({r['case_id'] for r in runs}) for arm in ['baseline', 'selected_skill']],
            'ae_host_status': 'NOT_RUN'}


def run_plan(plan_path, plan_sha256, catalog_path, standard_root, argv, runtime_roots, output, skill_package, skill_policy, usage_root=None):
    raw = Path(plan_path).read_bytes()
    require(digest(raw) == plan_sha256, 'protected plan digest mismatch')
    plan, catalog = load_json(plan_path), load_json(catalog_path)
    cases = validate_plan(plan, catalog)
    standard_files = snapshot(standard_root)
    require(not any(p.startswith(('starter-kit/fixtures/ai/', 'starter-kit/tests/', 'packages/agent-evaluation/')) or p in {'docs/AI_BEHAVIOR_SCENARIOS.md', 'docs/REFERENCE_AGENT_EVALUATION.md', 'docs/AGENT_EVALUATION_SOURCES.json'} or Path(p).name in {'expected.json', 'run.json', 'skill-evaluation-cases.json'} for p in standard_files), 'observer fixture/oracle files in agent snapshot')
    require('AI_ENTRYPOINT.md' in standard_files, 'standard entrypoint missing')
    require(digest(standard_files) == plan['standard_snapshot_sha256'], 'provided standard snapshot changed')
    selected = plan['selected_skill']
    if not all(shutil.which(tool) is not None for tool in selected['available_tools']):
        raise agent_skills.SkillError('declared required tool executable unavailable', 'BLOCKED')
    inv, entry = agent_skills.authorize(skill_package, selected['source_commit'], skill_policy, selected['policy_sha256'], plan['standard_commit'])
    require(inv['package_sha256'] == selected['package_sha256'] and inv['name'] == selected['name'], 'selected package identity changed')
    def skill_loader(name):
        resource = agent_skills.load_resource(skill_package, name, selected['source_commit'], skill_policy, selected['policy_sha256'], plan['standard_commit'], selected['task'], selected['available_tools'])
        require(len(resource['content'].encode()) <= MAX_BYTES, 'resource exceeds evaluation protocol budget')
        return resource
    skill_bytes = skill_loader('SKILL.md')['content'].encode()
    require(digest({'argv': argv, 'runtime_roots': runtime_roots, 'model': plan['model']}) == plan['agent_configuration_sha256'], 'agent configuration changed')
    out = Path(output).resolve()
    require(not out.exists(), 'new observer output directory required')
    out.mkdir(parents=False)
    require(not any(out.is_relative_to(Path(p).resolve()) or Path(p).resolve().is_relative_to(out) for p in runtime_roots), 'runtime scope overlaps observer output')
    runs = []
    experiment_id = uuid.uuid4().hex
    for case in cases:
        for repetition in range(plan['repetitions']):
            for arm in ['baseline', 'selected_skill']:
                run_id = experiment_id + '-' + case['id'] + '-' + str(repetition) + '-' + arm
                with tempfile.TemporaryDirectory(prefix='ae-agent-visible-') as temporary, tempfile.TemporaryDirectory(prefix='ae-agent-checkers-') as checker_temporary:
                    checker_root = Path(checker_temporary).resolve()
                    for name,content in case['observer_files'].items():
                        dest=safe_path(checker_root,name);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content)
                    visible = Path(temporary).resolve(); project = visible / 'project'; project.mkdir()
                    for name, content in case['files'].items():
                        dest = safe_path(project, name); dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(content)
                    # Caller supplies a sanitized standard snapshot, excluding observer fixture/catalog/test files.
                    shutil.copytree(standard_root, visible / 'standard', symlinks=False)
                    require(digest(snapshot(visible / 'standard')) == plan['standard_snapshot_sha256'], 'standard changed during preparation')
                    try:
                        private = [out, Path(plan_path), Path(catalog_path), Path(skill_policy), Path(skill_package)]
                        if usage_root:
                            private.append(Path(usage_root))
                        isolation = Isolation([visible], runtime_roots, private + [checker_root])
                        checker_isolation = Isolation([project,checker_root],runtime_roots,private)
                        isolation.probe(sys.executable, project)
                        broker = Broker(case, project, isolation, skill_bytes.decode() if arm == 'selected_skill' else None, plan, skill_loader if arm == 'selected_skill' else None, checker_root, checker_isolation)
                        run = launch_agent(argv, broker, visible, plan, run_id, arm)
                    except IsolationUnavailable as exc:
                        run = {'run_id': run_id, 'status': 'BLOCKED', 'mode': plan['mode'], 'scope': 'isolation-unavailable', 'duration_ms': None, 'critical_violation': False, 'reason': str(exc)}
                    run.update({'case_id': case['id'], 'arm': arm, 'repetition': repetition, 'partition': plan['partition'], 'agent_configuration_sha256': plan['agent_configuration_sha256'], 'standard_snapshot_sha256': plan['standard_snapshot_sha256'], 'standard_commit': plan['standard_commit'], 'catalog_sha256': plan['catalog_sha256'], 'selected_skill_sha256': plan['selected_skill']['package_sha256'] if arm == 'selected_skill' else None})
                    provider = Path(usage_root) / (run_id + '.json') if usage_root else None
                    run['usage'] = usage_receipt(provider if provider and provider.is_file() and run['status'] not in {'BLOCKED', 'NOT_RUN'} else None, run_id, plan['agent_configuration_sha256'])
                    (out / (run_id + '.json')).write_text(json.dumps(run, ensure_ascii=False, indent=2) + '\n')
                    runs.append(run)
    report = compare_runs(runs)
    (out / 'record.json').write_text(json.dumps({'schema_version': 1, 'experiment_id': experiment_id, 'runs': runs, 'comparison': report}, ensure_ascii=False, indent=2) + '\n')
    (out / 'comparison.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', required=True); p.add_argument('--plan-sha256', required=True); p.add_argument('--catalog', required=True)
    p.add_argument('--standard-snapshot', required=True); p.add_argument('--skill-package', required=True); p.add_argument('--skill-policy', required=True); p.add_argument('--output', required=True)
    p.add_argument('--runtime-root', action='append', default=[]); p.add_argument('--usage-root'); p.add_argument('agent_argv', nargs=argparse.REMAINDER)
    args = p.parse_args()
    try:
        argv = args.agent_argv[1:] if args.agent_argv[:1] == ['--'] else args.agent_argv
        report = run_plan(args.plan, args.plan_sha256, args.catalog, args.standard_snapshot, argv, args.runtime_root, args.output, args.skill_package, args.skill_policy, args.usage_root)
        print(json.dumps(report, ensure_ascii=False)); return 0 if report['status'] in {'PASS', 'SYNTHETIC_PASS'} else 1
    except (ValueError, OSError, UnicodeError, TypeError, KeyError) as exc:
        print(json.dumps({'status': getattr(exc, 'status', 'FAIL'), 'scope': 'evaluation-input', 'error': str(exc)})); return 1


if __name__ == '__main__':
    sys.exit(main())
