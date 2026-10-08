import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import check_task_execution as taskcheck
import check_native_review as nativecheck
import check_native_examples as examples

CANDIDATE = 'a' * 40

class ExecutionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / 'result.log').write_text('actual test output')
        ev = {'id': 'E-1', 'path': 'result.log', 'sha256': hashlib.sha256(b'actual test output').hexdigest(), 'candidate': CANDIDATE}
        self.task = {'id': 'task-1', 'owner': 'one', 'acceptance': 'observable criterion', 'status': 'DONE',
                     'allowed_paths': ['src/math.cpp'], 'depends_on': [], 'ready_conditions': [{'condition': 'approved existing scope', 'met': True}],
                     'budget': {'unit': 'minutes', 'limit': 10, 'spent': 4}, 'resources': [],
                     'result': {'candidate': CANDIDATE, 'summary': 'result', 'changed_paths': ['src/math.cpp'], 'evidence_ids': ['E-1']}}
        self.record = {'schema_version': 1, 'candidate': CANDIDATE, 'tasks': [self.task], 'evidence': [ev],
                       'integration_checks': [{'id': 'unit', 'candidate': CANDIDATE, 'status': 'PASS', 'evidence_ids': ['E-1']}],
                       'review': {'candidate': CANDIDATE, 'reviewer': 'one', 'spec': {'status': 'PASS', 'basis': 'acceptance verified'},
                                  'quality': {'status': 'PASS', 'basis': 'scope inspected'}, 'findings': []}}
    def run_record(self):
        return taskcheck.validate(self.record, self.root, CANDIDATE, ['unit'])
    def rejected(self):
        with self.assertRaises(ValueError): self.run_record()
    def test_small_single_owner_no_second_agent(self):
        self.assertEqual(self.run_record()['status'], 'PASS')
        self.assertFalse(self.run_record()['host_certified'])
    def test_unknown_dependency(self):
        self.task['depends_on'] = ['missing']; self.rejected()
    def test_cyclic_dependency(self):
        other = copy.deepcopy(self.task); other['id'] = 'task-2'; other['depends_on'] = ['task-1']; self.task['depends_on'] = ['task-2']
        self.record['tasks'].append(other); self.rejected()
    def test_dependency_not_ready(self):
        other = copy.deepcopy(self.task); other['id'] = 'task-2'; other['status'] = 'TODO'; self.task['depends_on'] = ['task-2']
        self.record['tasks'].append(other); self.rejected()
    def test_unmet_readiness(self):
        self.task['ready_conditions'][0]['met'] = False; self.rejected()
    def test_budget_exhausted(self):
        self.task['budget']['spent'] = 11; self.rejected()
    def test_negative_and_bool_budget(self):
        for value in (-1, True):
            self.task['budget']['spent'] = value; self.rejected()
    def test_unknown_format_fields_rejected(self):
        self.record['permit_unsafe'] = True; self.rejected()
        del self.record['permit_unsafe']; self.task['unbounded_budget'] = True; self.rejected()
    def test_wrong_result_and_resource_types_rejected(self):
        self.task['result']['evidence_ids'] = 'E-1'; self.rejected()
        self.task['result']['evidence_ids'] = ['E-1']; self.task['resources'] = [{'kind': 'device', 'key': 'x', 'mode': False}]; self.rejected()
    def test_missing_owner(self):
        self.task['owner'] = ''; self.rejected()
    def test_delegated_write_outside_scope(self):
        self.task['result']['changed_paths'] = ['src/other.cpp']; self.rejected()
    def test_path_traversal(self):
        self.task['allowed_paths'] = ['src/../secrets']; self.rejected()
    def test_parallel_write_overlap(self):
        self.task['status'] = 'RUNNING'
        other = copy.deepcopy(self.task); other['id'] = 'task-2'; other['allowed_paths'] = ['src']
        self.record['tasks'].append(other); self.rejected()
    def resource_pair(self, left, right):
        self.task['status'] = 'RUNNING'; self.task['resources'] = [left]
        other = copy.deepcopy(self.task); other['id'] = 'task-2'; other['allowed_paths'] = ['src/other.cpp']; other['resources'] = [right]
        self.record['tasks'].append(other)
    def test_device_cannot_be_shared_exclusive(self):
        self.resource_pair({'kind': 'device', 'key': 'AE-owned-session', 'mode': 'exclusive'}, {'kind': 'device', 'key': 'AE-owned-session', 'mode': 'read'}); self.rejected()
    def test_cache_and_output_ancestor_conflict(self):
        for kind in ('cache', 'output'):
            saved = copy.deepcopy(self.record)
            self.resource_pair({'kind': kind, 'key': 'build', 'mode': 'exclusive'}, {'kind': kind, 'key': 'build/job', 'mode': 'read'}); self.rejected()
            self.record = saved; self.task = self.record['tasks'][0]
    def test_readonly_cache_can_share_but_unfinished_not_pass(self):
        r = {'kind': 'cache', 'key': 'cache', 'mode': 'read'}; self.resource_pair(r, r)
        self.assertEqual(self.run_record()['status'], 'BLOCKED')
    def test_parallel_results_need_combined_candidate_check(self):
        self.record['integration_checks'][0]['candidate'] = 'b' * 40; self.rejected()
    def test_missing_required_check(self):
        self.record['integration_checks'] = []; self.rejected()
    def test_unavailable_check_never_pass(self):
        self.record['integration_checks'][0].update(status='NOT_RUN', reason='AE unavailable')
        self.assertEqual(self.run_record()['status'], 'BLOCKED')
    def test_separate_spec_and_quality_outcomes(self):
        self.record['review']['quality']['status'] = 'FAIL'
        self.assertEqual(self.run_record()['status'], 'FAIL')
        del self.record['review']['spec']; self.rejected()
    def test_actionable_blocker_cannot_be_averaged(self):
        self.record['review']['findings'] = [{'location': 'src/math.cpp:4', 'consequence': 'overflow', 'basis': 'boundary input fixture', 'blocking': True, 'resolved': False}]
        self.assertEqual(self.run_record()['status'], 'FAIL')
    def test_resolved_blocker_needs_current_resolution_evidence(self):
        self.record['review']['findings'] = [{'location': 'src/math.cpp:4', 'consequence': 'overflow', 'basis': 'boundary input fixture', 'blocking': True, 'resolved': True}]
        self.rejected()
        self.record['review']['findings'][0]['resolution_evidence_ids'] = ['E-1']
        self.assertEqual(self.run_record()['status'], 'PASS')
    def test_bool_schema_version_rejected(self):
        self.record['schema_version'] = True; self.rejected()
    def test_finding_requires_location_consequence_basis(self):
        self.record['review']['findings'] = [{'location': '', 'consequence': 'bad', 'basis': 'test', 'blocking': False, 'resolved': False}]; self.rejected()
    def test_evidence_tamper(self):
        (self.root / 'result.log').write_text('changed'); self.rejected()
    def test_old_evidence_not_new_candidate(self):
        self.record['evidence'][0]['candidate'] = 'b' * 40; self.rejected()
    def test_symlink_evidence(self):
        (self.root / 'link').symlink_to(self.root / 'result.log'); self.record['evidence'][0]['path'] = 'link'; self.rejected()
    def test_duplicate_json_and_nan_rejected(self):
        for data in ('{"a":1,"a":2}', '{"a":NaN}'):
            path = self.root / 'bad.json'; path.write_text(data)
            with self.assertRaises(ValueError): taskcheck.read_json(path)

class NativeReviewTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup); self.root = Path(tmp.name)
        (self.root / 'source.cpp').write_text('original local source')
        (self.root / 'review.log').write_text('review and unit test receipt')
        ev = {'id': 'E', 'path': 'review.log', 'sha256': hashlib.sha256(b'review and unit test receipt').hexdigest(), 'candidate': CANDIDATE}
        areas = {key: {'status': 'PASS', 'basis': 'actual bounded source inspection', 'evidence_ids': ['E']} for key in nativecheck.AREAS}
        self.record = {'schema_version': 1, 'candidate': CANDIDATE, 'evidence': [ev], 'inventory': [{'path': 'source.cpp', 'sha256': hashlib.sha256(b'original local source').hexdigest(), 'status': 'REVIEWED', 'basis': 'scope inspected', 'areas': areas}],
                       'unit_contracts': [{'quantity': 'time', 'input_unit': 'frame', 'output_unit': 'second', 'conversion': 'frames / fps', 'invariant': 'seconds * fps == frames within selected tolerance', 'evidence_ids': ['E']}]}
    def run_record(self): return nativecheck.validate(self.record, self.root, CANDIDATE, ['source.cpp'])
    def test_scoped_native_review_consistency_only(self):
        self.assertEqual(self.run_record()['status'], 'PASS'); self.assertFalse(self.run_record()['sdk_certified'])
    def test_unreviewed_section_remains_gap(self):
        self.record['inventory'][0]['status'] = 'UNREVIEWED'; self.assertEqual(self.run_record()['status'], 'BLOCKED')
    def test_concurrency_not_run_remains_gap(self):
        self.record['inventory'][0]['areas']['concurrency'].update(status='NOT_RUN', basis='thread sanitizer unavailable'); self.assertEqual(self.run_record()['status'], 'BLOCKED')
    def test_omitted_coverage_rejected(self):
        self.record['inventory'] = []
        with self.assertRaises(ValueError): self.run_record()
    def test_source_new_bytes_invalidate_review(self):
        (self.root / 'source.cpp').write_text('new candidate bytes')
        with self.assertRaises(ValueError): self.run_record()
    def test_stale_evidence_rejected(self):
        self.record['evidence'][0]['candidate'] = 'b' * 40
        with self.assertRaises(ValueError): self.run_record()
    def test_native_area_failure_is_fail(self):
        self.record['inventory'][0]['areas']['memory']['status'] = 'FAIL'
        self.assertEqual(self.run_record()['status'], 'FAIL')
    def test_malformed_unreviewed_areas_rejected(self):
        self.record['inventory'][0].update(status='UNREVIEWED', areas='malformed')
        with self.assertRaises(ValueError): self.run_record()
    def test_native_unknown_fields_rejected(self):
        self.record['host_certified'] = True
        with self.assertRaises(ValueError): self.run_record()
    def test_missing_ownership_review(self):
        del self.record['inventory'][0]['areas']['ownership']
        with self.assertRaises(ValueError): self.run_record()
    def test_units_need_actual_contract(self):
        self.record['unit_contracts'] = []
        with self.assertRaises(ValueError): self.run_record()
    def test_units_contract_needs_conversion(self):
        self.record['unit_contracts'][0]['conversion'] = ''
        with self.assertRaises(ValueError): self.run_record()

class NativeExecutionTests(unittest.TestCase):
    def test_missing_compiler_explicit_blocked(self):
        report = examples.run_examples('ae-rules-compiler-that-does-not-exist')
        self.assertEqual(report['status'], 'BLOCKED'); self.assertEqual(report['host_status'], 'NOT_RUN')
    def test_property_fuzz_and_original_defect_red_green(self):
        report = examples.run_examples()
        if report['status'] == 'BLOCKED':
            self.skipTest(report['reason'])
        self.assertEqual(report['status'], 'PASS', report)
        self.assertTrue(report['regression_detected_original'])
        self.assertTrue(report['invalid_units_compile_rejected'])
        self.assertEqual(report['iterations'], 20000)
        self.assertEqual(report['runs'][0]['exit_code'], 0)
        self.assertEqual(report['runs'][1]['exit_code'], 1)
        self.assertEqual(report['host_status'], 'NOT_RUN')

if __name__ == '__main__': unittest.main()
