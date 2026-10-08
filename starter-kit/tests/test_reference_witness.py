import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from test_reference_obligations import sample, SCRIPTS
import check_reference_witness as w

class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger, policy = sample(self.root)
        self.manifest = {"schema_version":1,"policy":policy,"reviewer_id":"reviewer",
            "review_status":"APPROVED","reviewed_at":"2026-01-02T00:00:00Z",
            "expires_at":"2099-01-01T00:00:00Z","captures":[]}
        obligation = self.ledger["obligations"][0]
        for role in ("original_cases", "fixtures", "verifier"):
            records = [obligation[role]] if role == "verifier" else obligation[role]
            for record in records:
                self.manifest["captures"].append({"evidence_id":record["evidence_id"],"obligation_id":obligation["id"],
                    "role":role,"record_sha256":hashlib.sha256(w.canonical(record)).hexdigest(),
                    "owner_sha256":hashlib.sha256(w.canonical(obligation["owner"])).hexdigest(),
                    "runner_id":"separate observer","review_status":"APPROVED"})
        self.pin = hashlib.sha256(w.canonical(self.manifest)).hexdigest()
    def check(self, repin=False):
        pin = hashlib.sha256(w.canonical(self.manifest)).hexdigest() if repin else self.pin
        return w.verify(self.ledger,self.manifest,pin,self.root,"a"*40)
    def test_matching_witness(self):
        self.assertEqual(self.check(),[])
    def test_pin_cannot_come_from_candidate(self):
        self.manifest["captures"][0]["runner_id"] = "forged"
        self.assertTrue(self.check())
    def test_witness_must_run_ledger_and_hash_checks(self):
        (self.root/"capture.txt").write_text("tampered")
        self.assertTrue(self.check())
    def test_missing_evidence_root(self):
        self.assertTrue(w.verify(self.ledger,self.manifest,self.pin))
    def test_empty_ledger_is_not_vacuous_pass(self):
        for ledger in ({},[],{"obligations":[]},None):
            self.assertTrue(w.verify(ledger,self.manifest,self.pin,self.root,"a"*40))
    def test_omitted_or_unrequired_obligation(self):
        self.ledger["obligations"][0]["required"] = False
        self.assertTrue(self.check())
    def test_unwitnessed(self):
        self.manifest["captures"].pop()
        self.assertTrue(self.check(repin=True))
    def test_unapproved_or_unauthorized_review(self):
        for field, value in (("review_status","PENDING"),("reviewer_id","")):
            before = self.manifest[field]
            self.manifest[field] = value
            self.assertTrue(self.check(repin=True))
            self.manifest[field] = before
        self.manifest["captures"][0]["runner_id"] = "reviewer"
        self.assertTrue(self.check(repin=True))
    def test_expired_or_future_approval(self):
        self.manifest["expires_at"] = "2026-01-03T00:00:00Z"
        self.assertTrue(self.check(repin=True))
        self.manifest["reviewed_at"] = "2099-01-01T00:00:00Z"
        self.assertTrue(self.check(repin=True))
    def test_replayed_candidate(self):
        self.assertTrue(w.verify(self.ledger,self.manifest,self.pin,self.root,"b"*40))
    def test_binding_includes_scope_role_environment_procedure(self):
        record = self.ledger["obligations"][0]["verifier"]
        for field, value in (("environment","other host"),("run_id","old run"),("command","made up"),
                             ("tool_version","2"),("observed_at","2026-01-01T01:00:00Z")):
            with self.subTest(field=field):
                before = record[field]
                record[field] = value
                self.assertTrue(self.check())
                record[field] = before
        self.manifest["captures"][0]["role"] = "fixtures"
        self.assertTrue(self.check(repin=True))
    def test_changed_path_and_reference(self):
        self.ledger["reference"]["sha256"] = "b"*64
        self.assertTrue(self.check())
    def test_missing_or_wrong_owner_binding_fails_closed(self):
        for capture in self.manifest['captures']:
            capture.pop('owner_sha256')
        self.assertTrue(self.check(repin=True))
        for capture in self.manifest['captures']:
            capture['owner_sha256'] = 'b'*64
        self.assertTrue(self.check(repin=True))

    def test_owner_substitution_same_revision_and_bytes_is_rejected(self):
        owner = self.ledger['obligations'][0]['owner']
        (self.root/'src/other').write_bytes((self.root/'src/main').read_bytes())
        owner['path'] = 'src/other'
        self.assertTrue(self.check())

    def test_duplicate_extra_capture(self):
        self.manifest["captures"].append(dict(self.manifest["captures"][0]))
        self.assertTrue(self.check(repin=True))
        self.manifest["captures"][-1]["evidence_id"] = "unrelated"
        self.assertTrue(self.check(repin=True))
    def test_invalid_manifest_and_pin(self):
        for manifest in (None,[],1):
            self.assertTrue(w.verify(self.ledger,manifest,self.pin,self.root))
        for pin in ("",None,[],"x"*64):
            self.assertTrue(w.verify(self.ledger,self.manifest,pin,self.root))
    def test_cli_valid_and_forged_pass(self):
        ledger, witness = self.root/"ledger.json", self.root/"witness.json"
        ledger.write_text(json.dumps(self.ledger))
        witness.write_text(json.dumps(self.manifest))
        cmd = [sys.executable,str(SCRIPTS/"check_reference_witness.py"),str(ledger),"--protected-manifest",str(witness),
               "--expected-manifest-sha256",self.pin,"--evidence-root",str(self.root),"--expected-candidate-revision","a"*40]
        result = subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse(json.loads(result.stdout)["parity_certified"])
        ledger.write_text('{}')
        result = subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(result.returncode,1,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"],"FAIL")
        self.assertNotIn("separate observer",result.stdout)

if __name__ == "__main__":
    unittest.main()
