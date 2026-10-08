"""Synthetic adapter contracts, including actual local fixture subprocesses. No model/AE runs."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import agent_evaluation as e
import check_agent_evaluation as verifier

PACK = Path(__file__).resolve().parents[1] / 'fixtures/ai/skill-evaluation-cases.json'


class SyntheticIsolation:
    """Test-only wrapper; deliberately not offered by the production launcher."""
    def wrap(self, argv, cwd):
        return [sys.executable if argv[0] == 'python3' else argv[0], *argv[1:]]


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.case = copy.deepcopy(e.load_json(PACK)['cases'][0])
        self.project = self.root / 'project'; self.project.mkdir()
        self.checkers=self.root/'observer-checkers';self.checkers.mkdir()
        for name,content in self.case['observer_files'].items():
            p=self.checkers/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(content)
        for name, content in self.case['files'].items():
            p = self.project / name; p.parent.mkdir(exist_ok=True, parents=True); p.write_text(content)
        self.plan = {'schema_version':1, 'partition':'tune', 'standard_commit':'a'*40,
                     'catalog_sha256':e.digest(e.load_json(PACK)), 'agent_configuration_sha256':'b'*64,
                     'standard_snapshot_sha256':'c'*64, 'case_ids':[self.case['id']], 'repetitions':2,
                     'max_actions':20, 'repair_budget':3, 'no_progress_limit':2, 'timeout_s':5,
                     'selected_skill':{'name':'fixture-review', 'package_sha256':'d'*64, 'policy_sha256':'e'*64, 'source_commit':'f'*40,'task':'package-audit','available_tools':['python3']},
                     'model':'synthetic-protocol-fixture', 'mode':'SYNTHETIC'}
        if os.name == 'nt':
            checker=patch.object(e,'controlled_check',return_value={'alias':'product','exit_code':0,'duration_ms':0.0,'status':'PASS','stdout_sha256':'a'*64,'stderr_sha256':'b'*64,'output':'synthetic Windows contract response'})
            checker.start();self.addCleanup(checker.stop)

    def broker(self, case=None, skill=None):
        return e.Broker(case or self.case, self.project, SyntheticIsolation(), skill, self.plan, checker_root=self.checkers)

    def observed_run(self, arm='baseline', passed=True):
        broker = self.broker(skill='fixture skill' if arm == 'selected_skill' else None)
        broker.handle({'op':'read','path':'src/product.json'})
        if arm == 'selected_skill':
            broker.handle({'op':'select_skill'})
        broker.handle({'op':'write','path':'src/product.json','content':'{"value":7}'})
        broker.handle({'op':'finish','message':'fixture done; AE NOT_RUN','claims':{'runtime_status':'NOT_RUN'}})
        objectives=e.objective_results(self.case,self.project,broker,arm)
        if not passed:
            objectives[1]['status']='FAIL'
        return {'run_id':arm+'-1','case_id':self.case['id'],'arm':arm,'repetition':0,'partition':'tune',
                'mode':'SYNTHETIC','status':'SYNTHETIC_PASS' if passed else 'FAIL', 'scope':'adapter-contract-only',
                'duration_ms':1.0,'critical_violation':False,'violations':[], 'objectives':objectives,'action_receipts':broker.receipts,
                'usage':{'status':'NOT_RUN','tokens':None,'cost':None},'agent_configuration_sha256':'b'*64,
                'standard_snapshot_sha256':'c'*64,'catalog_sha256':'d'*64,'standard_commit':'a'*40,
                'selected_skill_sha256':'e'*64 if arm=='selected_skill' else None}

    def test_pack_has_disjoint_partitions_positive_negative_russian(self):
        catalog=e.load_json(PACK)
        for case in catalog['cases']:
            self.assertEqual(e.case_errors(case), [])
        self.assertEqual({c['partition'] for c in catalog['cases']}, {'tune','select','final'})
        for partition in e.PARTITIONS:
            self.assertEqual({c['should_select_skill'] for c in catalog['cases'] if c['partition']==partition},{True,False})
            self.assertTrue(all(any('\u0400'<=ch<='\u04ff' for ch in c['request']) for c in catalog['cases'] if c['partition']==partition))

    def test_plan_pin_case_partition_budget_and_frozen_final(self):
        self.assertEqual(len(e.validate_plan(self.plan,e.load_json(PACK))),1)
        for key,value in [('catalog_sha256','a'*64),('partition','final'),('max_actions',0),('repetitions',1000)]:
            plan=copy.deepcopy(self.plan);plan[key]=value
            with self.assertRaises(ValueError):e.validate_plan(plan,e.load_json(PACK))
        final=next(c for c in e.load_json(PACK)['cases'] if c['partition']=='final')
        plan=copy.deepcopy(self.plan);plan.update(partition='final',case_ids=[final['id']],selected_configuration_sha256='b'*64,oracle_exposed_to_configuration=False)
        self.assertEqual(len(e.validate_plan(plan,e.load_json(PACK))),1)
        plan['oracle_exposed_to_configuration']=True
        with self.assertRaises(ValueError):e.validate_plan(plan,e.load_json(PACK))

    def test_reject_duplicate_case_and_mutable_unreviewed_skill(self):
        catalog=e.load_json(PACK);catalog['cases'].append(catalog['cases'][0]);self.plan['catalog_sha256']=e.digest(catalog)
        with self.assertRaises(ValueError):e.validate_plan(self.plan,catalog)
        self.plan['catalog_sha256']=e.digest(e.load_json(PACK));self.plan['selected_skill']['package_sha256']='not-a-digest'
        with self.assertRaises(ValueError):e.validate_plan(self.plan,e.load_json(PACK))

    def test_unsafe_paths_symlink_and_protected_write_attempt(self):
        for name in ['../private','/tmp/private','src/../STATUS','src\\STATUS','.git/config']:
            with self.assertRaises(ValueError):e.safe_path(self.project,name)
        if hasattr(os,'symlink'):
            try:
                os.symlink(self.project/'src/product.json',self.project/'link')
            except OSError:
                pass  # Windows capability unavailable; portable path/protected-write checks still run.
            else:
                with self.assertRaises(ValueError):e.safe_path(self.project,'link',True)
        broker=self.broker();original=(self.checkers/'check.py').read_bytes()
        self.assertEqual(broker.handle({'op':'write','path':'tests/check.py','content':'pass'})['status'],'FAIL')
        self.assertEqual((self.checkers/'check.py').read_bytes(),original)
        self.assertFalse((self.project/'tests/check.py').exists())
        self.assertEqual(self.broker().handle({'op':'read','path':'tests/check.py'})['status'],'FAIL')
        self.assertTrue(broker.violations)

    def test_forbidden_command_records_attempt_without_execution(self):
        broker=self.broker()
        with patch.object(e,'controlled_check') as checker:
            result=broker.handle({'op':'command','argv':['publish','now']})
            self.assertEqual(result['status'],'FAIL');checker.assert_not_called()
        self.assertEqual(broker.receipts[0]['request']['op'],'command')

    def test_negative_selection_hard_failure_baseline_unavailable(self):
        case=copy.deepcopy(e.load_json(PACK)['cases'][1])
        broker=self.broker(case,skill='irrelevant')
        self.assertEqual(broker.handle({'op':'select_skill'})['status'],'FAIL')
        baseline=self.broker()
        self.assertEqual(baseline.handle({'op':'select_skill'})['status'],'BLOCKED')
        self.assertFalse(baseline.violations)

    def test_progressive_resource_rechecks_loader_and_denies_without_selection(self):
        calls=[]
        def loader(path):
            calls.append(path)
            if len(calls)>1:raise ValueError('package changed')
            return {'status':'PASS','content':'sealed skill','sha256':'a'*64}
        broker=e.Broker(self.case,self.project,SyntheticIsolation(),'available',self.plan,loader)
        self.assertEqual(broker.handle({'op':'select_skill'})['status'],'PASS')
        self.assertEqual(broker.handle({'op':'read_skill_resource','path':'references/api.md'})['status'],'FAIL')
        self.assertEqual(calls,['SKILL.md','references/api.md'])
        broker=self.broker()
        self.assertEqual(broker.handle({'op':'read_skill_resource','path':'SKILL.md'})['status'],'FAIL')

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix process monitoring required; Windows agent isolation unsupported')
    def test_real_controlled_check_and_bounded_no_progress(self):
        broker=self.broker()
        broker.handle({'op':'write','path':'src/product.json','content':'{"value":7}'})
        for _ in range(2):self.assertEqual(broker.handle({'op':'check','alias':'product'})['status'],'PASS')
        self.assertEqual(broker.handle({'op':'check','alias':'product'})['status'],'FAIL')
        self.assertEqual(len(broker.checks),3)
        self.assertIn('budget',broker.violations[0])
        self.assertTrue(broker.checks[0]['stdout_sha256']);self.assertEqual(broker.checks[0]['exit_code'],0)

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix process monitoring required; Windows agent isolation unsupported')
    def test_check_output_budget_and_descendant_timeout(self):
        case=copy.deepcopy(self.case);case['checks']['product']=[sys.executable,'-c','print("x"*2000000)']
        result=e.controlled_check('product',case,self.project,SyntheticIsolation(),checker_root=self.checkers)
        self.assertEqual(result['status'],'BLOCKED');self.assertIn('output budget',result['reason'])
        case['checks']['product']=[sys.executable,'-c','import time;time.sleep(5)']
        result=e.controlled_check('product',case,self.project,SyntheticIsolation(),timeout=.05,checker_root=self.checkers)
        self.assertEqual(result['status'],'BLOCKED');self.assertIn('timeout',result['reason'])

    def test_distinct_successful_checks_do_not_exhaust_repair_budget(self):
        broker = self.broker()
        broker.case['checks'] = {alias: ['unused'] for alias in ('unit', 'lint', 'types', 'package')}
        with patch.object(e, 'controlled_check', return_value={'status': 'PASS', 'exit_code': 0}):
            for alias in broker.case['checks']:
                self.assertEqual(broker.handle({'op': 'check', 'alias': alias})['status'], 'PASS')
        self.assertFalse(broker.violations)

    def test_changed_check_outcome_is_progress_and_alternating_aliases_still_bounded(self):
        broker = self.broker()
        with patch.object(e, 'controlled_check', side_effect=[{'status':'FAIL', 'exit_code':1},
                                                            {'status':'PASS', 'exit_code':0},
                                                            {'status':'PASS', 'exit_code':0}]):
            self.assertEqual(broker.handle({'op':'check', 'alias':'product'})['status'], 'FAIL')
            self.assertEqual(broker.handle({'op':'check', 'alias':'product'})['status'], 'PASS')
            self.assertEqual(broker.handle({'op':'check', 'alias':'product'})['status'], 'PASS')
        broker = self.broker()
        broker.case['checks']['lint'] = ['unused']
        with patch.object(e, 'controlled_check', return_value={'status':'FAIL', 'exit_code':1}):
            for alias in ('product','lint','product','lint'):
                broker.handle({'op':'check', 'alias':alias})
            self.assertIn('budget', broker.handle({'op':'check', 'alias':'product'})['reason'])

    def test_fake_pass_typed_claim_fails_independent_objective(self):
        broker=self.broker()
        broker.handle({'op':'finish','message':'AE PASS','claims':{'runtime_status':'PASS'}})
        checks=e.objective_results(self.case,self.project,broker,'baseline')
        claim=next(c for c in checks if c['id']=='no-fake-runtime-pass')
        self.assertEqual(claim['status'],'FAIL');self.assertTrue(claim['critical'])

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix process monitoring required; Windows agent isolation unsupported')
    def test_real_synthetic_subprocess_records_actual_actions(self):
        script=self.root/'protocol_fixture.py'
        script.write_text('import json,sys\np=json.loads(sys.stdin.readline())\nfor request in [{"op":"read","path":"src/product.json"},{"op":"write","path":"src/product.json","content":"{\\"value\\":7}"},{"op":"check","alias":"product"},{"op":"finish","message":"pure fixture complete; AE NOT_RUN","claims":{"runtime_status":"NOT_RUN"}}]:\n print(json.dumps(request),flush=True)\n json.loads(sys.stdin.readline())\n')
        broker=self.broker()
        run=e.launch_agent([sys.executable,str(script)],broker,self.root,self.plan,'independent-test','baseline')
        self.assertEqual(run['status'],'SYNTHETIC_PASS');self.assertEqual(len(run['action_receipts']),4)
        self.assertFalse(run['agent_effectiveness_certified']);self.assertFalse(run['ae_host_certified'])
        self.assertGreater(run['duration_ms'],0)

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix process monitoring required; Windows agent isolation unsupported')
    def test_missing_agent_finish_and_protocol_duplicates_fail(self):
        script=self.root/'bad_protocol.py';script.write_text('print(\'{"op":"finish","op":"write"}\',flush=True)\n')
        run=e.launch_agent([sys.executable,str(script)],self.broker(),self.root,self.plan,'bad','baseline')
        self.assertEqual(run['status'],'FAIL');self.assertTrue(run['critical_violation'])

    def test_usage_unknown_not_zero_cost_and_replay_rejected(self):
        self.assertIsNone(e.usage_receipt(None,'r','b'*64)['cost'])
        p=self.root/'usage.json';base={'run_id':'r','configuration_sha256':'b'*64,'authority':'provider','request_ids':['req-1'],'tokens':10,'cost':.1,'currency':'USD'}
        p.write_text(json.dumps(base));self.assertEqual(e.usage_receipt(p,'r','b'*64)['tokens'],10)
        for key,value in [('run_id','old'),('authority','agent'),('cost',-1),('tokens',float('nan')),('request_ids',['r','r'])]:
            mutated={**base,key:value};p.write_text(json.dumps(mutated))
            with self.assertRaises(ValueError):e.usage_receipt(p,'r','b'*64)

    def test_comparison_critical_and_noncritical_fail_not_averageable(self):
        rows=[self.observed_run(),self.observed_run('selected_skill')]
        self.assertEqual(e.compare_runs(rows)['status'],'SYNTHETIC_PASS')
        self.assertEqual(e.compare_runs(rows)['live_agent_status'],'NOT_RUN')
        rows[0]=self.observed_run(passed=False)
        self.assertEqual(e.compare_runs(rows)['status'],'FAIL')
        rows[0]['status']='SYNTHETIC_PASS'
        with self.assertRaises(ValueError):e.compare_runs(rows)
        rows[0]=self.observed_run();rows[0]['violations']=['publish attempt'];rows[0]['critical_violation']=True;rows[0]['status']='FAIL'
        self.assertEqual(e.compare_runs(rows)['status'],'FAIL')

    def test_comparison_rejects_identity_arm_mode_usage_and_critical_suppression(self):
        rows=[self.observed_run(),self.observed_run('selected_skill')]
        for key,value in [('mode','LIVE'),('selected_skill_sha256','changed'),('agent_configuration_sha256','a'*64),('critical_violation',True),('duration_ms',-1)]:
            changed=copy.deepcopy(rows);changed[1][key]=value
            with self.assertRaises(ValueError):e.compare_runs(changed)
        with self.assertRaises(ValueError):e.compare_runs(rows[:1])
        changed=copy.deepcopy(rows);changed[0]['usage']={'status':'NOT_RUN','tokens':0,'cost':0}
        with self.assertRaises(ValueError):e.compare_runs(changed)

    def test_both_synthetic_arms_cannot_be_relabeled_live_even_with_new_seal(self):
        rows=[self.observed_run(),self.observed_run('selected_skill')]
        for row in rows:row['mode']='LIVE'
        with self.assertRaises(ValueError):e.compare_runs(rows)
        data={'schema_version':1,'runs':rows,'comparison':{'status':'PASS','live_agent_status':'RUN'}}
        p=self.root/'relabeled.json';p.write_text(json.dumps(data))
        with self.assertRaises(ValueError):verifier.validate_record(p,e.digest(p.read_bytes()))
        for row in rows:row['status']='PASS'
        with self.assertRaises(ValueError):e.compare_runs(rows) # adapter-contract-only scope is still synthetic.

    def test_invalid_observer_identity_and_timestamp_rejected(self):
        rows=[self.observed_run(),self.observed_run('selected_skill')]
        for field,value in [('catalog_sha256','not-a-sha'),('standard_commit',True),('standard_snapshot_sha256',None)]:
            corrupted=copy.deepcopy(rows);corrupted[0][field]=value
            with self.assertRaises(ValueError):e.compare_runs(corrupted)
        rows[0]['action_receipts'][0]['started_at']='yesterday'
        with self.assertRaises(ValueError):e.compare_runs(rows)

    def test_record_seal_and_consistency_detect_changed_results(self):
        rows=[self.observed_run(),self.observed_run('selected_skill')]
        data={'schema_version':1,'runs':rows,'comparison':e.compare_runs(rows)}
        p=self.root/'record.json';p.write_text(json.dumps(data));sha=e.digest(p.read_bytes())
        self.assertEqual(verifier.validate_record(p,sha)['live_agent_status'],'NOT_RUN')
        data['runs'][0]['status']='PASS';p.write_text(json.dumps(data))
        with self.assertRaises(ValueError):verifier.validate_record(p,sha)
        with self.assertRaises(ValueError):verifier.validate_record(p,e.digest(p.read_bytes()))

    def test_run_plan_uses_real_package_admission_then_marks_missing_isolation_blocked(self):
        from test_agent_skills import SkillTests, CANDIDATE, SOURCE
        package_fixture=SkillTests(methodName='test_admitted_package_passes_without_executing_script')
        package_fixture.setUp();self.addCleanup(package_fixture.doCleanups)
        package_fixture.policy['entries'][0]['required_tools']=[]
        policy_pin=package_fixture.write_policy()
        standard=self.root/'rules';standard.mkdir();(standard/'AI_ENTRYPOINT.md').write_text('Owned synthetic adopted rules snapshot')
        plan=copy.deepcopy(self.plan)
        plan.update(standard_commit=CANDIDATE,standard_snapshot_sha256=e.digest(e.snapshot(standard)))
        argv=[sys.executable,'-c','print("must not run without isolation")']
        plan['agent_configuration_sha256']=e.digest({'argv':argv,'runtime_roots':[],'model':plan['model']})
        plan['selected_skill']={'name':'sample-skill','source_commit':SOURCE,'package_sha256':e.agent_skills.inventory(package_fixture.package)['package_sha256'],'policy_sha256':policy_pin,'task':'package-audit','available_tools':[]}
        p=self.root/'plan.json';p.write_text(json.dumps(plan))
        with patch.object(e,'Isolation',side_effect=e.IsolationUnavailable('test isolation unavailable')):
            report=e.run_plan(p,e.digest(p.read_bytes()),PACK,standard,argv,[],self.root/'observer',package_fixture.package,package_fixture.policy_file)
        self.assertEqual(report['status'],'BLOCKED')
        self.assertIsNone(report['arms']['baseline']['mean_duration_ms'])
        record=e.load_json(self.root/'observer/record.json')
        self.assertTrue(all(r['usage']['cost'] is None and r['status']=='BLOCKED' for r in record['runs']))
        self.assertEqual(verifier.validate_record(self.root/'observer/record.json',e.digest((self.root/'observer/record.json').read_bytes()))['status'],'BLOCKED')
        (package_fixture.package/'resources/guide.txt').write_text('changed after approval')
        with self.assertRaises(ValueError):
            e.run_plan(p,e.digest(p.read_bytes()),PACK,standard,argv,[],self.root/'observer-two',package_fixture.package,package_fixture.policy_file)
        self.assertFalse((self.root/'observer-two').exists())

    @unittest.skipIf(os.name == 'nt', 'NOT_RUN: Unix subprocess monitoring required')
    def test_run_plan_paired_subprocess_uses_hidden_observer_checkers(self):
        from test_agent_skills import SkillTests,CANDIDATE,SOURCE
        fixture=SkillTests(methodName='test_admitted_package_passes_without_executing_script');fixture.setUp();self.addCleanup(fixture.doCleanups)
        fixture.policy['entries'][0]['required_tools']=[];pin=fixture.write_policy()
        standard=self.root/'rules';standard.mkdir();(standard/'AI_ENTRYPOINT.md').write_text('Synthetic adopted rules')
        script=self.root/'paired_protocol.py'
        script.write_text('import json,sys\np=json.loads(sys.stdin.readline())\nassert "tests/check.py" not in p["files"]\nrequests=[{"op":"read","path":"src/product.json"}]\nif p["selected_skill_available"]:requests.append({"op":"select_skill"})\nrequests.extend([{"op":"write","path":"src/product.json","content":"{\\"value\\":7}"},{"op":"check","alias":"product"},{"op":"finish","message":"AE NOT_RUN","claims":{"runtime_status":"NOT_RUN"}}])\nfor request in requests:\n print(json.dumps(request),flush=True)\n json.loads(sys.stdin.readline())\n')
        # This test wrapper intentionally supplies no OS isolation: results must stay SYNTHETIC_PASS.
        class TestIsolation(SyntheticIsolation):
            def __init__(self,*args):pass
            def probe(self,*args):pass
        plan=copy.deepcopy(self.plan);plan['repetitions']=1
        plan.update(standard_commit=CANDIDATE,standard_snapshot_sha256=e.digest(e.snapshot(standard)))
        argv=[sys.executable,str(script)];plan['agent_configuration_sha256']=e.digest({'argv':argv,'runtime_roots':[],'model':plan['model']})
        plan['selected_skill']={'name':'sample-skill','source_commit':SOURCE,'package_sha256':e.agent_skills.inventory(fixture.package)['package_sha256'],'policy_sha256':pin,'task':'package-audit','available_tools':[]}
        p=self.root/'paired-plan.json';p.write_text(json.dumps(plan))
        with patch.object(e,'Isolation',TestIsolation):
            report=e.run_plan(p,e.digest(p.read_bytes()),PACK,standard,argv,[],self.root/'paired-output',fixture.package,fixture.policy_file)
        self.assertEqual(report['status'],'SYNTHETIC_PASS');self.assertEqual(report['live_agent_status'],'NOT_RUN')
        record=e.load_json(self.root/'paired-output/record.json')
        self.assertEqual(len(record['runs']),2)
        self.assertTrue(all(r['objectives'][-1]['status']=='PASS' for r in record['runs']))
        self.assertEqual(verifier.validate_record(self.root/'paired-output/record.json',e.digest((self.root/'paired-output/record.json').read_bytes()))['status'],'PASS')

    def test_run_plan_rejects_hidden_oracle_in_provided_standard(self):
        standard=self.root/'unsafe-rules';standard.mkdir();(standard/'AI_ENTRYPOINT.md').write_text('rules')
        (standard/'expected.json').write_text('{"hidden":"answer"}')
        plan=copy.deepcopy(self.plan);plan['standard_snapshot_sha256']=e.digest(e.snapshot(standard))
        p=self.root/'plan.json';p.write_text(json.dumps(plan))
        with self.assertRaisesRegex(ValueError,'oracle'):
            e.run_plan(p,e.digest(p.read_bytes()),PACK,standard,[],[],self.root/'observer','missing-package','missing-policy')
        self.assertFalse((self.root/'observer').exists())

    def test_runtime_cannot_overlap_any_observer_plan_catalog_policy(self):
        observer=self.root/'observer';observer.mkdir()
        private=self.root/'sealed-plan.json';private.write_text('{}')
        visible=self.root/'visible';visible.mkdir()
        with self.assertRaises(ValueError):e.Isolation([visible],[self.root],[observer,private])

    def test_absent_isolation_is_explicit_blocked(self):
        observer=self.root/'observer';observer.mkdir();visible=self.root/'visible';visible.mkdir()
        with patch.object(e.shutil,'which',return_value=None):
            with self.assertRaises(e.IsolationUnavailable):e.Isolation([visible],[],[observer])


if __name__ == '__main__':
    unittest.main()
