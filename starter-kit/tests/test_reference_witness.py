import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "scripts" / "check_reference_witness.py"
spec = importlib.util.spec_from_file_location("witness", path)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.record = {"evidence_id":"E1","artifact_sha256":"a"*64,"artifact_path":"capture.bin"}
        self.ledger = {"candidate_revision":"rev1","reference":{"sha256":"b"*64},
            "obligations":[{"required":True,"original_cases":[dict(self.record)],
                            "fixtures":[dict(self.record)],"verifier":dict(self.record, revision="rev1", authority="host")}]}
        self.manifest = {"schema_version":1,"candidate_revision":"rev1","reference_sha256":"b"*64,
            "captures":[dict(self.record,run_id="run1",runner_id="trusted",observed_at="2026-10-08T08:00:00Z",
                             authority="host",review_status="APPROVED",revision="rev1")]}
    def check(self, digest=None):
        return w.verify(self.ledger,self.manifest,digest or hashlib.sha256(w.canonical(self.manifest)).hexdigest())
    def test_matching_witness(self):
        self.assertEqual(self.check(),[])
    def test_unpinned_manifest(self):
        self.assertTrue(self.check("0"*64))
    def test_unwitnessed(self):
        self.manifest["captures"]=[]
        self.assertTrue(self.check())
    def test_unapproved(self):
        self.manifest["captures"][0]["review_status"]="PENDING"
        self.assertTrue(self.check())
    def test_stale_revision(self):
        self.manifest["captures"][0]["revision"]="old"
        self.assertTrue(self.check())
    def test_substituted_digest(self):
        self.manifest["captures"][0]["artifact_sha256"]="f"*64
        self.assertTrue(self.check())
    def test_missing_runner(self):
        del self.manifest["captures"][0]["runner_id"]
        self.assertTrue(self.check())
    def test_invalid_trusted_pin(self):
        self.assertTrue(self.check("not-a-digest"))
    def test_verifier_authority_mismatch(self):
        self.ledger["obligations"][0]["verifier"]["authority"] = "device"
        self.assertTrue(self.check())
    def test_duplicate_witness(self):
        self.manifest["captures"].append(dict(self.manifest["captures"][0]))
        self.assertTrue(self.check())

if __name__ == "__main__":
    unittest.main()
