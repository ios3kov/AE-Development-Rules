"""Correction regressions: owned synthetic files/processes, no live model or AE."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import test_agent_skills as skill_fixtures
import test_agent_evaluation as evaluation_fixtures
import test_engineering_execution as execution_fixtures
from test_reference_obligations import sample, SCRIPTS
import test_trusted_skill_workflow as workflow_fixtures
import agent_skills as skills
import agent_evaluation as evaluation
import check_reference_witness as witness


class CorrectionTests(unittest.TestCase):
    def fixture(self, cls, method):
        fixture = cls(methodName=method)
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    @unittest.skipIf(os.name == 'nt' or getattr(os, 'geteuid', lambda: 0)() == 0,
                     'NOT_RUN: actual POSIX directory denial requires non-root Unix')
    def test_unreadable_directory_cannot_return_inventory_or_complete_scan(self):
        f = self.fixture(skill_fixtures.SkillTests, 'test_admitted_package_passes_without_executing_script')
        directory = f.package / 'resources'
        directory.chmod(0)
        try:
            for operation in (skills.inventory, skills.scan):
                with self.subTest(operation=operation.__name__):
                    with self.assertRaises(skills.SkillError):
                        operation(f.package)
        finally:
            directory.chmod(0o700)

    @unittest.skipIf(os.name == 'nt' or getattr(os, 'geteuid', lambda: 0)() == 0,
                     'NOT_RUN: actual POSIX directory denial requires non-root Unix')
    def test_unreadable_package_cli_has_no_complete_report_or_digest(self):
        f = self.fixture(skill_fixtures.SkillTests, 'test_admitted_package_passes_without_executing_script')
        directory = f.package / 'resources'
        directory.chmod(0)
        try:
            run = subprocess.run([sys.executable, str(SCRIPTS / 'agent_skills.py'), 'scan', '--package', str(f.package)],
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 2)
            report = json.loads(run.stdout)
            self.assertEqual(report['status'], 'BLOCKED')
            self.assertNotIn('package_sha256', report)
            self.assertNotIn('files', report)
        finally:
            directory.chmod(0o700)

    def test_enumeration_error_is_fail_closed_on_all_platforms(self):
        f = self.fixture(skill_fixtures.SkillTests, 'test_admitted_package_passes_without_executing_script')
        scandir = os.scandir
        def fail_subdirectory(path):
            if Path(path) == f.package / 'resources':
                raise PermissionError('owned fixture directory denied')
            return scandir(path)
        with patch.object(skills.os, 'scandir', side_effect=fail_subdirectory):
            with self.assertRaises(skills.SkillError):
                skills.scan(f.package)

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix agent process monitoring required')
    def test_response_backpressure_obeys_agent_deadline(self):
        f = self.fixture(evaluation_fixtures.EvaluationTests, 'test_real_synthetic_subprocess_records_actual_actions')
        (f.project / 'src/product.json').write_text('x' * 200000)
        script = f.root / 'nonreading_agent.py'
        script.write_text('import json,sys,time\nsys.stdin.readline()\nprint(json.dumps({"op":"read","path":"src/product.json"}),flush=True)\ntime.sleep(4)\n')
        f.case['objectives'] = []
        f.plan['timeout_s'] = 1
        started = time.monotonic()
        run = evaluation.launch_agent([sys.executable, str(script)], f.broker(), f.root, f.plan, 'response-backpressure')
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual(run['status'], 'FAIL')
        self.assertIn('agent timeout', run['violations'])

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix agent process monitoring required')
    def test_initial_message_backpressure_obeys_deadline_and_cleans_up(self):
        f = self.fixture(evaluation_fixtures.EvaluationTests, 'test_real_synthetic_subprocess_records_actual_actions')
        script = f.root / 'nonreading_initial_agent.py'
        script.write_text('import signal,time\nsignal.signal(signal.SIGTERM,signal.SIG_IGN)\ntime.sleep(4)\n')
        f.case.update(context=['x' * 200000], objectives=[])
        f.plan['timeout_s'] = 1
        started = time.monotonic()
        run = evaluation.launch_agent([sys.executable, str(script)], f.broker(), f.root, f.plan, 'initial-backpressure')
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual(run['status'], 'FAIL')
        self.assertIn('agent timeout', run['violations'])

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix agent process monitoring required')
    def test_broker_command_uses_remaining_agent_deadline(self):
        f = self.fixture(evaluation_fixtures.EvaluationTests, 'test_real_synthetic_subprocess_records_actual_actions')
        f.case['checks']['product'] = [sys.executable, '-c', 'import time;time.sleep(4)']
        f.case['objectives'] = []
        script = f.root / 'checking_agent.py'
        script.write_text('import json,sys\nsys.stdin.readline()\nprint(json.dumps({"op":"check","alias":"product"}),flush=True)\nsys.stdin.readline()\n')
        f.plan['timeout_s'] = 1
        started = time.monotonic()
        run = evaluation.launch_agent([sys.executable, str(script)], f.broker(), f.root, f.plan, 'command-deadline')
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual(run['status'], 'FAIL')
        self.assertEqual(run['action_receipts'][0]['result']['reason'], 'command timeout')

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix agent process monitoring required')
    def test_large_startup_and_response_are_delivered_without_truncation(self):
        f = self.fixture(evaluation_fixtures.EvaluationTests, 'test_real_synthetic_subprocess_records_actual_actions')
        content = 'Unicode fixture: ж\n' * 20000
        (f.project / 'src/product.json').write_text(content)
        f.case.update(context=['context' * 30000], objectives=[])
        script = f.root / 'large_protocol_agent.py'
        script.write_text('import json,sys\np=json.loads(sys.stdin.readline())\nassert p["context"]==["context"*30000]\n'
                          'print(json.dumps({"op":"read","path":"src/product.json"}),flush=True)\n'
                          'r=json.loads(sys.stdin.readline())\nassert r["content"]=="Unicode fixture: ж\\n"*20000\n'
                          'print(json.dumps({"op":"finish","message":"bounded fixture complete","claims":{}}),flush=True)\n'
                          'assert json.loads(sys.stdin.readline())["status"]=="PASS"\n')
        run = evaluation.launch_agent([sys.executable, str(script)], f.broker(), f.root, f.plan, 'large-success')
        self.assertEqual(run['status'], 'SYNTHETIC_PASS')
        self.assertEqual(len(run['action_receipts']), 2)

    def test_cache_output_conflicts_share_filesystem_namespace(self):
        for left, right in [('build', 'build'), ('build', 'build/job'), ('build/job', 'build')]:
            for kinds in [('cache', 'output'), ('output', 'cache')]:
                with self.subTest(paths=(left, right), kinds=kinds):
                    f = self.fixture(execution_fixtures.ExecutionTests, 'test_small_single_owner_no_second_agent')
                    f.resource_pair({'kind': kinds[0], 'key': left, 'mode': 'exclusive'},
                                    {'kind': kinds[1], 'key': right, 'mode': 'read'})
                    with self.assertRaises(ValueError):
                        f.run_record()

    def test_disjoint_and_readonly_cross_kind_resources_remain_valid(self):
        for left, right, mode in [('build/a', 'build/b', 'exclusive'), ('build', 'build/job', 'read')]:
            f = self.fixture(execution_fixtures.ExecutionTests, 'test_small_single_owner_no_second_agent')
            f.resource_pair({'kind': 'cache', 'key': left, 'mode': mode}, {'kind': 'output', 'key': right, 'mode': 'read'})
            self.assertEqual(f.run_record()['status'], 'BLOCKED')  # unfinished tasks

    def test_reference_dispatch_requires_separate_evidence_commit(self):
        f = self.fixture(workflow_fixtures.WorkflowInputs, 'test_reference_backwards_compatibility_and_skill_subject')
        self.assertEqual(f.check(REVIEW_MODE='reference', EVIDENCE_SHA='c' * 40), 0)
        for sha in ['', 'main', 'c' * 39, 'C' * 40, '$(false)']:
            self.assertNotEqual(f.check(REVIEW_MODE='reference', EVIDENCE_SHA=sha), 0)
        self.assertEqual(f.check(REVIEW_MODE='skills', EVIDENCE_SHA=''), 0)
        self.assertNotEqual(f.check(REVIEW_MODE='', EVIDENCE_SHA=''), 0)
        self.assertIn('ref: ${{ inputs.evidence_sha }}', f.body)
        self.assertIn('"evidence/$LEDGER_PATH"', f.body)
        self.assertIn('--evidence-root evidence --candidate-root candidate', f.body)
        self.assertNotRegex(f.body, r'(?:python\S*|node|bash)\s+evidence/')

    def test_source_commit_precedes_evidence_commit_and_owner_uses_source(self):
        if shutil.which('git') is None:
            self.skipTest('NOT_RUN: Git fixture unavailable')
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name).resolve()
        repo = root / 'evidence'; repo.mkdir()
        ledger, policy = sample(repo)
        # Commit source S before creating reports that refer to S.
        def git(*args):
            return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                                   '-c', 'user.name=Owned fixture', '-c', 'user.email=fixture@example.invalid', *args],
                                  cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
        git('init', '-q'); git('add', 'src/main'); git('commit', '-qm', 'source S')
        source_sha = git('rev-parse', 'HEAD')
        candidate = root / 'candidate'
        git('clone', '--no-hardlinks', '-q', str(repo), str(candidate))
        ledger['candidate_revision'] = policy['candidate_revision'] = source_sha
        item = ledger['obligations'][0]; item['owner']['revision'] = source_sha
        for record in item['fixtures'] + [item['verifier']]:
            record['revision'] = source_sha
        report = json.loads((repo / 'verifier.json').read_text()); report['revision'] = source_sha
        (repo / 'verifier.json').write_text(json.dumps(report))
        item['verifier']['artifact_sha256'] = hashlib.sha256((repo / 'verifier.json').read_bytes()).hexdigest()
        manifest = {'schema_version': 1, 'policy': policy, 'reviewer_id': 'independent reviewer',
                    'review_status': 'APPROVED', 'reviewed_at': '2026-01-02T00:00:00Z',
                    'expires_at': '2099-01-01T00:00:00Z', 'captures': []}
        for role in ('original_cases', 'fixtures', 'verifier'):
            records = [item[role]] if role == 'verifier' else item[role]
            for record in records:
                manifest['captures'].append({'evidence_id': record['evidence_id'], 'obligation_id': item['id'],
                                            'role': role, 'record_sha256': hashlib.sha256(witness.canonical(record)).hexdigest(),
                                            'runner_id': 'owned synthetic observer', 'review_status': 'APPROVED'})
        pin = hashlib.sha256(witness.canonical(manifest)).hexdigest()
        (repo / 'ledger.json').write_text(json.dumps(ledger))
        # E can store a different source tree; only S supplies owner bytes.
        (repo / 'src/main').write_text('unrelated source bytes in evidence storage')
        git('add', 'src/main', 'capture.txt', 'verifier.json', 'ledger.json'); git('commit', '-qm', 'evidence E for source S')
        evidence_sha = git('rev-parse', 'HEAD'); self.assertNotEqual(source_sha, evidence_sha)
        # The old workflow's E-as-candidate check rejects an S-bound report.
        self.assertIn('candidate differs from trusted policy/checkout',
                      witness.verify(ledger, manifest, pin, repo, evidence_sha))
        protected = root / 'witness.json'; protected.write_text(json.dumps(manifest))
        argv = [sys.executable, str(SCRIPTS / 'check_reference_witness.py'), str(repo / 'ledger.json'),
                '--protected-manifest', str(protected), '--expected-manifest-sha256', pin,
                '--evidence-root', str(repo), '--candidate-root', str(candidate),
                '--expected-candidate-revision', source_sha]
        run = subprocess.run(argv, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        if os.name != 'nt' and workflow_fixtures.BASH is not None:
            # Execute the actual workflow verification step with owned synthetic
            # pins, both real Git checkouts and a trusted copy of checker code.
            f = self.fixture(workflow_fixtures.WorkflowInputs, 'test_reference_backwards_compatibility_and_skill_subject')
            block = f.body.split('      - name: Check ledger, local Evidence and independent witness together', 1)[1].split('      - name:', 1)[0]
            step = '\n'.join(line[10:] for line in block.split('        run: |\n', 1)[1].splitlines())
            trusted = root / 'trusted/starter-kit/scripts'; trusted.mkdir(parents=True)
            for name in ('check_reference_witness.py', 'check_reference_obligations.py'):
                shutil.copyfile(SCRIPTS / name, trusted / name)
            runner_temp = root / 'runner-temp'; runner_temp.mkdir()
            environment = {**os.environ, 'TRUSTED_WITNESS_JSON': json.dumps(manifest), 'TRUSTED_WITNESS_SHA256': pin,
                           'CANDIDATE_SHA': source_sha, 'EVIDENCE_SHA': evidence_sha,
                           'LEDGER_PATH': 'ledger.json', 'RUNNER_TEMP': str(runner_temp)}
            result = subprocess.run([workflow_fixtures.BASH, '-c', step], cwd=root, env=environment,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((runner_temp / 'reference-witness.json').exists())
            environment['EVIDENCE_SHA'] = source_sha
            result = subprocess.run([workflow_fixtures.BASH, '-c', step], cwd=root, env=environment,
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
        original = (candidate / 'src/main').read_bytes()
        (candidate / 'src/main').write_text('tampered reviewed source')
        run = subprocess.run(argv, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        (candidate / 'src/main').write_bytes(original)
        (repo / 'capture.txt').write_text('tampered evidence')
        run = subprocess.run(argv, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main()
