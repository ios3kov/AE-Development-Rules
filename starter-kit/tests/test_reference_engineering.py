import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_reference_obligations import SCRIPTS
import reference_engineering as r
import reference_ui as ui

class EngineeringTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'observation').write_text('synthetic')
        self.observations={"inventory":["save","cancel"],"observations":[{"behavior_id":"save","case_id":"save-positive",
            "claim_status":"OBSERVED","artifact_path":"observation","artifact_sha256":hashlib.sha256(b'synthetic').hexdigest(),
            "evidence_id":"E-save","preconditions":{},"input":{},"action":"save","expected":{"state":"saved"},"environment":"fixture"}]}
    def test_generate_and_report_missing_observations(self):
        report=r.compile_observations(self.observations,self.root)
        self.assertEqual(report['status'],'BLOCKED')
        self.assertEqual(report['unobserved_behaviors'],['cancel'])
        self.assertEqual(report['execution_status'],'NOT_RUN')
        self.observations['inventory']=['save']
        self.assertEqual(r.compile_observations(self.observations,self.root)['status'],'PASS')
    def test_inferred_and_tampered_oracle_rejected(self):
        self.observations['observations'][0]['claim_status']='INFERRED'
        with self.assertRaises(ValueError): r.compile_observations(self.observations,self.root)
        self.observations['observations'][0]['claim_status']='OBSERVED'
        (self.root/'observation').write_text('changed')
        with self.assertRaises(ValueError): r.compile_observations(self.observations,self.root)
    def test_first_divergence_order_cancel_recovery(self):
        trace={'reference_environment':'matched','candidate_environment':'matched','reference':['start','cancel','recover'],'candidate':['start','recover','cancel']}
        self.assertEqual(r.compare_traces(trace)['first_divergence'],1)
        trace['candidate']=trace['reference'][:]
        self.assertEqual(r.compare_traces(trace)['status'],'PASS')
        trace['candidate'].append(None)
        self.assertEqual(r.compare_traces(trace)['first_divergence'],3)
    def test_environment_mismatch(self):
        with self.assertRaises(ValueError):r.compare_traces({'reference':[],'candidate':[]})
    def test_graph_cross_layer_and_unknown(self):
        graph={'nodes':[{'id':'UI','layer':'screen','claim_status':'OBSERVED','evidence_id':'E-1'},
            {'id':'Native','layer':'process','claim_status':'UNKNOWN'}],'edges':[{'from':'UI','to':'Native','claim_status':'INFERRED'}]}
        report=r.graph(graph)
        self.assertEqual(report['unknown_nodes'],['Native'])
        self.assertIn('INFERRED',report['mermaid'])
        graph['edges'][0]['to']='missing'
        with self.assertRaises(ValueError):r.graph(graph)
    def test_version_diff_selects_impacted_obligations(self):
        data={'before':{'artifact_sha256':'a'*64,'components':{'func':{'sha256':'b'*64,'obligation_ids':['O1']}}},
              'after':{'artifact_sha256':'c'*64,'components':{'func':{'sha256':'d'*64,'obligation_ids':['O1','O2']}}}}
        report=r.version_diff(data)
        self.assertEqual(report['rerun_obligations'],['O1','O2'])
        self.assertTrue(report['reuse_requires_review'])
    def test_route_by_bytes_and_capability(self):
        binary=self.root/'misleading.json'
        binary.write_bytes(b'\xcf\xfa\xed\xfe' + b'fixture')
        caps={'tools':[{'name':'ghidra','version':'fixture-1','operations':['decompile','xrefs'],'probe_status':'PASS'}]}
        self.assertEqual(r.route(binary,caps)['kind'],'mach-o')
        caps['tools'][0]['operations']=['decompile']
        self.assertEqual(r.route(binary,caps)['status'],'BLOCKED')
    def test_retry_and_cost_are_measured_without_agent_pass(self):
        call={'tool':'ghidra','operation':'decompile','input_digest':'a'*64,'usable':False,'tokens':20,'cost':0.01}
        report=r.metrics({'calls':[call,dict(call)],'expected_first_tool':'ghidra','selected_first_tool':'browser'})
        self.assertEqual(report['unjustified_repeats'],1)
        self.assertEqual(report['tokens'],40)
        self.assertFalse(report['first_tool_matches_plan'])
        self.assertFalse(report['agent_behavior_certified'])
    def test_unknown_usage_is_not_zero(self):
        with self.assertRaises(ValueError):r.metrics({'calls':[{'tool':'t','operation':'o','input_digest':'d','tokens':None,'cost':0}]})
    def image(self):
        return dict(width=2,height=1,bit_depth=32,color_space='linear',alpha_mode='straight',device='fixture',viewport=[2,1],scale=1,
                    font_identity='fixture',render_path='synthetic',rgba=[2.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0])
    def test_pixels_alpha_hdr_and_full_scope(self):
        a=self.image()
        data={'reference':a,'candidate':copy.deepcopy(a),'regions':[{'id':'right','x':1,'y':0,'width':1,'height':1}]}
        self.assertEqual(ui.compare(data)['status'],'PASS')
        data['candidate']['rgba'][3]=1.0
        report=ui.compare(data)
        self.assertEqual(report['status'],'FAIL')
        self.assertEqual(report['regions'][0]['changed_channels'],0)
        self.assertTrue(report['alpha_preserved'])
    def test_pixels_mismatch_nonfinite_and_bad_regions(self):
        data={'reference':self.image(),'candidate':self.image(),'regions':[{'id':'full','x':0,'y':0,'width':2,'height':1}]}
        data['candidate']['color_space']='different'
        with self.assertRaises(ValueError):ui.compare(data)
        data['candidate']=self.image()
        data['candidate']['rgba'][0]=float('nan')
        with self.assertRaises(ValueError):ui.compare(data)
    def test_observed_tokens(self):
        result=ui.tokens({'controls':[{'evidence_id':'E1','colors':['#FFFFFF','#ffffff'],'spacing':[8],'font_sizes':[12]}]})
        self.assertEqual(result['tokens']['colors'],['#ffffff'])
        with self.assertRaises(ValueError):ui.tokens({'controls':[{'colors':['#ffffff']}]})
    def test_contrast_exact_threshold(self):
        self.assertEqual(ui.contrast({'foreground':'#000000','background':'#ffffff','minimum_ratio':4.5})['ratio'],21)
        self.assertEqual(ui.contrast({'foreground':'#ffffff','background':'#ffffff','minimum_ratio':4.5})['status'],'FAIL')
    def test_cli_blocks_and_returns_nonzero(self):
        data=self.root/'trace.json'
        data.write_text(json.dumps({'reference_environment':'fixture','candidate_environment':'fixture','reference':['cancel'],'candidate':['success']}))
        result=subprocess.run([sys.executable,str(SCRIPTS/'reference_engineering.py'),'compare',str(data)],capture_output=True,text=True)
        self.assertEqual(result.returncode,1,result.stderr+result.stdout)
        self.assertEqual(json.loads(result.stdout)['first_divergence'],0)
        data.write_text('[]')
        result=subprocess.run([sys.executable,str(SCRIPTS/'reference_ui.py'),'compare',str(data)],capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertEqual(json.loads(result.stdout)['status'],'FAIL')

if __name__=='__main__':unittest.main()
