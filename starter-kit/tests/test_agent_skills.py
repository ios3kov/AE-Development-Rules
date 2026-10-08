import copy
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
import agent_skills as s

CANDIDATE = 'b'*40
SOURCE = 'a'*40

class SkillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.package = self.base/'candidate'/'sample-skill'
        self.package.mkdir(parents=True)
        self.skill('sample-skill')
        (self.package/'resources').mkdir()
        (self.package/'resources'/'guide.txt').write_text('owned synthetic instructions',encoding='utf-8')
        (self.package/'scripts').mkdir()
        (self.package/'scripts'/'demo.py').write_text("raise RuntimeError('MUST NEVER EXECUTE')",encoding='utf-8')
        self.policy_file = self.base/'protected-policy.json'
        self.policy = self.make_policy()
        self.pin = self.write_policy()
        self.install_root = self.base/'installed'
    def skill(self,name):
        (self.package/'SKILL.md').write_text('---\nname: '+name+'\ndescription: Synthetic owned fixture for package verification.\nmetadata:\n  origin: owned-test\n---\nOnly read explicitly selected resources.\n',encoding='utf-8')
    def make_policy(self):
        inv = s.inventory(self.package)
        return {'schema_version':1,'candidate_revision':CANDIDATE,'exceptions':[],
                'telemetry_enabled':False,'entries':[{'name':inv['name'],'source':'fixture://owned',
                 'source_commit':SOURCE,'purpose':'synthetic package checks','license':'Owned fixture, tests only',
                 'package_sha256':inv['package_sha256'],'status':'allowed','tasks':['package-audit'],
                 'required_tools':['python3'],'isolation_profile':'static-read-only',
                 'review':{'reviewer_id':'independent-reviewer','submitter_id':'candidate-author','status':'APPROVED',
                           'reviewed_at':'2026-01-01T00:00:00Z','expires_at':'2099-01-01T00:00:00Z'},
                 'scan':{'status':'complete','scanner_id':'owned-fixture-scanner','runner_id':'independent-scanner',
                         'package_sha256':inv['package_sha256'],'files':inv['files'],'findings_reviewed':True,
                         'scanner_version':'1','config_sha256':'d'*64,'check_ids':['AGENT-SKILL-PACKAGE-001'],'errors':[],'omissions':[]}}]}
    def write_policy(self):
        self.policy_file.write_bytes(s.canonical(self.policy))
        return s.digest(self.policy_file.read_bytes())
    def authorize(self,**kw):
        return s.authorize(self.package,SOURCE,self.policy_file,self.pin,CANDIDATE,**kw)
    def manage(self,action,**kw):
        kwargs = {'package':self.package,'source_commit':SOURCE,'policy_path':self.policy_file,
                  'expected_policy_sha256':self.pin,'candidate_revision':CANDIDATE}
        kwargs.update(kw)
        return s.manage(action,self.install_root,'project-owned-manager',**kwargs)
    def rejected(self,fn,status=None):
        with self.assertRaises(s.SkillError) as caught:
            fn()
        if status:
            self.assertEqual(caught.exception.status,status)
    def test_admitted_package_passes_without_executing_script(self):
        inv,_ = self.authorize()
        self.assertEqual(len(inv['files']),3)
        self.assertFalse((self.base/'executed').exists())
    def test_telemetry_does_not_disable_scan(self):
        self.policy['telemetry_enabled'] = False
        self.policy['entries'][0]['scan']['status'] = 'unavailable'
        self.pin = self.write_policy()
        self.rejected(self.authorize,'BLOCKED')
    def test_each_nonallowed_status_cannot_activate(self):
        for status in ('candidate','rejected','revoked'):
            self.policy['entries'][0]['status'] = status
            self.pin = self.write_policy()
            self.rejected(lambda:self.manage('install'),'BLOCKED')
            self.assertFalse(self.install_root.exists())
    def test_scan_incomplete_unavailable_fail_closed(self):
        for status in ('incomplete','unavailable'):
            self.policy['entries'][0]['scan']['status'] = status
            self.pin = self.write_policy()
            self.rejected(self.authorize,'BLOCKED')
    def test_missing_scanner_identity_denied(self):
        self.policy['entries'][0]['scan']['scanner_id'] = ''
        self.pin = self.write_policy()
        self.rejected(self.authorize,'BLOCKED')
    def test_candidate_cannot_review_or_scan_itself(self):
        for role,field in [('review','reviewer_id'),('scan','runner_id')]:
            before = copy.deepcopy(self.policy)
            self.policy['entries'][0][role][field] = 'candidate-author'
            self.pin = self.write_policy()
            self.rejected(self.authorize,'BLOCKED')
            self.policy = before
    def test_scan_covers_script_and_resource_not_just_skill(self):
        self.policy['entries'][0]['scan']['files'] = self.policy['entries'][0]['scan']['files'][:1]
        self.pin = self.write_policy()
        self.rejected(self.authorize)
    def test_modified_resource_invalidates_old_evidence(self):
        (self.package/'resources'/'guide.txt').write_text('changed')
        self.rejected(self.authorize)
    def test_added_file_invalidates_old_evidence(self):
        (self.package/'hidden-hook').write_text('hook')
        self.rejected(self.authorize)
    def test_removed_script_invalidates_old_evidence(self):
        (self.package/'scripts'/'demo.py').unlink()
        self.rejected(self.authorize)
    def test_source_revision_required_exact(self):
        self.rejected(lambda:s.authorize(self.package,'main',self.policy_file,self.pin,CANDIDATE))
        self.rejected(lambda:s.authorize(self.package,'c'*40,self.policy_file,self.pin,CANDIDATE))
    def test_policy_pin_external_and_candidate_cannot_weaken(self):
        self.policy['entries'][0]['required_tools'] = []
        self.write_policy()
        self.rejected(self.authorize)
    def test_policy_inside_package_or_checkout_is_denied(self):
        nested = self.package.parent/'approval.json'
        nested.write_bytes(self.policy_file.read_bytes())
        self.rejected(lambda:s.authorize(self.package,SOURCE,nested,self.pin,CANDIDATE,candidate_root=self.package.parent))
    def test_policy_inside_install_scope_is_denied(self):
        self.install_root.mkdir()
        nested = self.install_root/'policy.json'
        nested.write_bytes(self.policy_file.read_bytes())
        self.rejected(lambda:s.authorize(self.package,SOURCE,nested,self.pin,CANDIDATE,install_root=self.install_root))
    def test_exact_candidate_revision(self):
        self.rejected(lambda:s.authorize(self.package,SOURCE,self.policy_file,self.pin,'c'*40))
    def test_policy_exceptions_cannot_bypass_scan(self):
        self.policy['exceptions'] = [{'skip_scan':True}]
        self.pin = self.write_policy()
        self.rejected(self.authorize,'BLOCKED')
    def test_missing_license_is_not_chosen(self):
        for license in ('','unknown','undefined'):
            self.policy['entries'][0]['license'] = license
            self.pin = self.write_policy()
            self.rejected(self.authorize)
    def test_expired_future_review_denied(self):
        for key,value in [('expires_at','2001-01-01T00:00:00Z'),('reviewed_at','2098-01-01T00:00:00Z')]:
            self.policy['entries'][0]['review'][key] = value
            self.pin = self.write_policy()
            self.rejected(self.authorize,'BLOCKED')
    def test_unknown_fields_duplicate_names_rejected(self):
        self.policy['entries'].append(copy.deepcopy(self.policy['entries'][0]))
        self.pin = self.write_policy()
        self.rejected(self.authorize)
    def test_json_duplicate_keys_nonfinite_denied(self):
        for content in (b'{"a":1,"a":2}',b'{"a":NaN}'):
            self.policy_file.write_bytes(content)
            self.rejected(lambda:s.strict_json(self.policy_file))
    def test_isolation_unavailable_execution_is_blocked(self):
        self.rejected(lambda:self.authorize(isolation_profile='shell-sandbox'),'BLOCKED')
    def test_tools_and_task_selection_no_universal_gate(self):
        result = s.select(self.policy_file,self.pin,CANDIDATE,'small-edit',[])
        self.assertEqual(result['skills'],[])
        result = s.select(self.policy_file,self.pin,CANDIDATE,'package-audit',[])
        self.assertEqual(result['skills'][0]['status'],'BLOCKED')
        result = s.select(self.policy_file,self.pin,CANDIDATE,'package-audit',['python3'])
        self.assertEqual(result['skills'][0]['status'],'CANDIDATE')
    def test_progressive_resource_loading_only_selected_bytes(self):
        result = s.load_resource(self.package,'resources/guide.txt',SOURCE,self.policy_file,self.pin,CANDIDATE,'package-audit',['python3'])
        self.assertEqual(result['content'],'owned synthetic instructions')
        self.assertTrue(result['untrusted_material'])
        self.assertNotIn('demo.py',result['content'])
        self.rejected(lambda:s.load_resource(self.package,'../outside',SOURCE,self.policy_file,self.pin,CANDIDATE,'package-audit',['python3']))
    def test_load_cannot_skip_applicability_tools(self):
        for task,tools in [('small-edit',['python3']),('package-audit',[])]:
            self.rejected(lambda:s.load_resource(self.package,'SKILL.md',SOURCE,self.policy_file,self.pin,CANDIDATE,task,tools),'BLOCKED')
    def test_registry_supports_revoked_old_version_without_name_collision(self):
        previous = copy.deepcopy(self.policy['entries'][0])
        previous['package_sha256'] = 'e'*64
        previous['status'] = 'revoked'
        self.policy['entries'].append(previous)
        self.pin = self.write_policy()
        self.authorize()
    def test_scan_full_inventory_markers_no_safety_certificate(self):
        result = s.scan(self.package)
        self.assertEqual(result['scan_status'],'complete')
        self.assertFalse(result['security_certified'])
        self.assertEqual(result['files'],s.inventory(self.package)['files'])
    def test_standard_frontmatter_scalar_block_compatibility(self):
        data = b'---\nname: sample-skill\ndescription: >-\n  First line.\n  Second line.\ncompatibility: "Python 3.11"\nallowed-tools: Read Bash\nmetadata:\n  key: value\n---\nBody.'
        parsed = s.skill_metadata(data,'sample-skill')
        self.assertEqual(parsed['description'],'First line. Second line.')
        self.assertEqual(parsed['allowed-tools'],'Read Bash')
    def test_standard_name_description_boundaries(self):
        for name in ('Upper','-bad','bad-','bad--name','x'*65):
            self.rejected(lambda:s.skill_metadata(('---\nname: '+name+'\ndescription: text\n---').encode()))
        for desc in ('','x'*1025):
            self.rejected(lambda:s.skill_metadata(('---\nname: good\ndescription: "'+desc+'"\n---').encode()))
    def test_standard_name_must_match_directory(self):
        self.skill('other')
        self.rejected(lambda:s.inventory(self.package))
    def test_unsupported_yaml_blocked_not_new_format(self):
        self.rejected(lambda:s.skill_metadata(b'---\nname: sample-skill\ndescription: &anchor Example\n---'),'BLOCKED')

    def test_ambiguous_yaml_scalars_do_not_change_types(self):
        for raw in ('123', 'True', 'YES', '0xFF', '1.2', '2026-10-08', "'unescaped'quote'"):
            with self.subTest(raw=raw):
                self.rejected(lambda:s.yaml_string(raw), 'BLOCKED')
        self.assertEqual(s.yaml_string("'escaped''quote'"), "escaped'quote")
        self.assertEqual(s.yaml_string('"123"'), '123')
    def test_symlink_file_and_directory_denied(self):
        outside = self.base/'outside'
        outside.write_text('outside')
        link = self.package/'link'
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest('OS symlink creation unavailable; ZIP symlink denial remains tested')
        self.rejected(lambda:s.inventory(self.package))
        link.unlink()
        link.symlink_to(self.base,target_is_directory=True)
        self.rejected(lambda:s.inventory(self.package))
    def test_hardlink_denied(self):
        import os
        os.link(self.package/'SKILL.md',self.package/'hardlink')
        self.rejected(lambda:s.inventory(self.package))
    def test_case_collisions_denied(self):
        # Case-insensitive hosts cannot create distinct aliases; that OS already
        # enforces collision. ZIP case-collision test remains portable.
        (self.package/'Case').write_text('1')
        (self.package/'case').write_text('2')
        if len([p for p in self.package.iterdir() if p.name.lower()=='case']) == 2:
            self.rejected(lambda:s.inventory(self.package))
    def archive(self,records):
        path = self.base/'fixture.zip'
        with zipfile.ZipFile(path,'w') as archive:
            for name,data in records:
                archive.writestr(name,data)
        return path
    def test_bounded_local_import_good_restored_bytes(self):
        archive = self.archive([('SKILL.md',(self.package/'SKILL.md').read_bytes()),('resources/x','x')])
        dest = self.base/'imported'/'sample-skill'
        result = s.import_zip(archive,dest)
        self.assertEqual(result['package_sha256'],s.inventory(dest)['package_sha256'])
        self.assertEqual((dest/'resources/x').read_text(),'x')
    def test_archive_traversal_absolute_windows_reserved_denied(self):
        for name in ('../escape','/abs','a\\b','C:/x','a/./b','a//b','CON','a.','a '):
            path = self.archive([(name,'bad')])
            self.rejected(lambda:s.import_zip(path,self.base/'imported'/'sample-skill'))
        self.assertFalse((self.base/'escape').exists())
    def test_archive_duplicate_case_colliding_paths_denied(self):
        for records in ([('a','1'),('a','2')],[('A','1'),('a','2')]):
            path = self.archive(records)
            self.rejected(lambda:s.import_zip(path,self.base/'imported'/'sample-skill'))
    def test_archive_symlink_denied(self):
        path = self.base/'fixture.zip'
        info = zipfile.ZipInfo('link')
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK|0o777)<<16
        with zipfile.ZipFile(path,'w') as archive:
            archive.writestr(info,'../../target')
        self.rejected(lambda:s.import_zip(path,self.base/'imported'/'sample-skill'))
    def test_archive_size_bomb_denied_and_no_destination(self):
        path = self.base/'fixture.zip'
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('large','0'*(s.MAX_FILE+1))
        dest = self.base/'imported'/'sample-skill'
        self.rejected(lambda:s.import_zip(path,dest))
        self.assertFalse(dest.exists())
    def test_archive_existing_destination_preserved(self):
        path = self.archive([('SKILL.md',(self.package/'SKILL.md').read_bytes())])
        dest = self.base/'sample-skill'
        dest.mkdir()
        (dest/'foreign').write_text('keep')
        self.rejected(lambda:s.import_zip(path,dest))
        self.assertEqual((dest/'foreign').read_text(),'keep')
    def test_install_restore_and_owner_scope(self):
        self.manage('install')
        self.assertEqual(s.inventory(self.package)['package_sha256'],s.inventory(self.install_root/'sample-skill')['package_sha256'])
        self.rejected(lambda:s.owner_state(self.install_root,'another-owner'))
    def test_install_name_conflict(self):
        self.manage('install')
        self.rejected(lambda:self.manage('install'))
    def test_unowned_foreign_scope_preserved(self):
        self.install_root.mkdir()
        (self.install_root/'foreign').write_text('keep')
        self.rejected(lambda:self.manage('install'))
        self.assertEqual((self.install_root/'foreign').read_text(),'keep')
    def test_foreign_or_modified_package_files_preserved_on_remove(self):
        self.manage('install')
        target = self.install_root/'sample-skill'/'foreign'
        target.write_text('keep')
        self.rejected(lambda:s.manage('remove',self.install_root,'project-owned-manager',name='sample-skill'))
        self.assertEqual(target.read_text(),'keep')
        target.unlink()
        target = self.install_root/'sample-skill'/'resources'/'guide.txt'
        target.write_text('user change')
        self.rejected(lambda:s.manage('remove',self.install_root,'project-owned-manager',name='sample-skill'))
        self.assertEqual(target.read_text(),'user change')
    def test_safe_remove_preserves_unrelated_root_files(self):
        self.manage('install')
        (self.install_root/'foreign').write_text('keep')
        result = s.manage('remove',self.install_root,'project-owned-manager',name='sample-skill')
        self.assertEqual(result['status'],'PASS')
        self.assertEqual((self.install_root/'foreign').read_text(),'keep')
    def update_fixture(self):
        first = self.policy['entries'][0]['package_sha256']
        self.manage('install')
        (self.package/'resources'/'guide.txt').write_text('v2')
        self.policy = self.make_policy()
        self.pin = self.write_policy()
        self.manage('update')
        return first
    def test_managed_update_verified_rollback(self):
        first = self.update_fixture()
        historical = self.install_root/'.history'/'sample-skill'/first/'sample-skill'
        self.policy = self.make_policy()
        inv = s.inventory(historical)
        self.policy['entries'][0]['package_sha256'] = inv['package_sha256']
        self.policy['entries'][0]['scan']['package_sha256'] = inv['package_sha256']
        self.policy['entries'][0]['scan']['files'] = inv['files']
        self.pin = self.write_policy()
        self.manage('rollback',name='sample-skill',target_digest=first)
        self.assertEqual((self.install_root/'sample-skill'/'resources'/'guide.txt').read_text(),'owned synthetic instructions')
    def test_revoked_rollback_denied(self):
        first = self.update_fixture()
        self.policy['entries'][0]['status'] = 'revoked'
        self.pin = self.write_policy()
        self.rejected(lambda:self.manage('rollback',name='sample-skill',target_digest=first),'BLOCKED')
        self.assertEqual((self.install_root/'sample-skill'/'resources'/'guide.txt').read_text(),'v2')
    def test_rollback_history_tampering_denied(self):
        first = self.update_fixture()
        historical = self.install_root/'.history'/'sample-skill'/first/'sample-skill'
        (historical/'SKILL.md').write_text('tampered')
        self.rejected(lambda:self.manage('rollback',name='sample-skill',target_digest=first))
    def test_update_foreign_files_preserved(self):
        self.manage('install')
        (self.install_root/'sample-skill'/'foreign').write_text('keep')
        self.rejected(lambda:self.manage('update'))
    def test_empty_directories_affect_digest_and_restore(self):
        before = s.inventory(self.package)['package_sha256']
        (self.package/'empty').mkdir()
        self.assertNotEqual(before,s.inventory(self.package)['package_sha256'])
        self.policy = self.make_policy()
        self.pin = self.write_policy()
        self.manage('install')
        self.assertTrue((self.install_root/'sample-skill'/'empty').is_dir())
    def test_filesystem_dotdot_cannot_evade_policy_boundary(self):
        nested = self.package.parent/'policy.json'
        nested.write_bytes(self.policy_file.read_bytes())
        misleading = self.base/'elsewhere'/'..'/'candidate'/'policy.json'
        self.rejected(lambda:s.authorize(self.package,SOURCE,misleading,self.pin,CANDIDATE,candidate_root=self.package.parent))
    def test_modified_permission_mode_invalidates_inventory(self):
        if sys.platform == 'win32':
            self.skipTest('POSIX executable permission changes unavailable')
        (self.package/'scripts'/'demo.py').chmod(0o755)
        self.rejected(self.authorize)
    def test_corrupt_registry_cannot_escape_installation_scope(self):
        self.manage('install')
        registry_file = self.install_root/s.REGISTRY_FILE
        registry = s.strict_json(registry_file)
        registry['skills']['../foreign'] = registry['skills'].pop('sample-skill')
        registry_file.write_bytes(s.canonical(registry))
        self.rejected(lambda:s.manage('remove',self.install_root,'project-owned-manager',name='sample-skill'))
        self.assertTrue((self.install_root/'sample-skill'/'SKILL.md').exists())
    def test_archive_special_permission_bits_denied(self):
        path = self.base/'fixture.zip'
        info = zipfile.ZipInfo('script')
        info.create_system = 3
        info.external_attr = (stat.S_IFREG|0o4755)<<16
        with zipfile.ZipFile(path,'w') as archive:
            archive.writestr(info,'candidate')
        self.rejected(lambda:s.import_zip(path,self.base/'imported'/'sample-skill'))
    def test_concurrent_lifecycle_lock_blocks_without_mutation(self):
        self.manage('install')
        with s.lifecycle_lock(self.install_root):
            self.rejected(lambda:s.manage('remove',self.install_root,'project-owned-manager',name='sample-skill'),'BLOCKED')
            self.assertTrue((self.install_root/'sample-skill'/'SKILL.md').exists())
    def test_scan_error_omission_cannot_be_complete(self):
        for key in ('errors','omissions'):
            before = copy.deepcopy(self.policy)
            self.policy['entries'][0]['scan'][key] = ['not inspected']
            self.pin = self.write_policy()
            self.rejected(self.authorize,'BLOCKED')
            self.policy = before
    def test_scanner_version_config_mandatory(self):
        for key,value in [('scanner_version',''),('config_sha256','main'),('check_ids',[])]:
            before = copy.deepcopy(self.policy)
            self.policy['entries'][0]['scan'][key] = value
            self.pin = self.write_policy()
            self.rejected(self.authorize)
            self.policy = before
    @unittest.skipIf(sys.platform=='win32','POSIX special permission bits only')
    def test_special_permission_bits_denied(self):
        script = self.package/'scripts'/'demo.py'
        script.chmod(0o1755)
        self.rejected(lambda:s.inventory(self.package))
    def test_cli_errors_nonzero_and_no_certificate(self):
        result = subprocess.run([sys.executable,str(SCRIPTS/'agent_skills.py'),'check','--package',str(self.package),
            '--source-commit',SOURCE,'--policy',str(self.policy_file),'--expected-policy-sha256','0'*64,
            '--expected-candidate-revision',CANDIDATE],text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(json.loads(result.stdout)['security_certified'])

if __name__ == '__main__': unittest.main()
