import hashlib
import importlib.util
import pathlib
import tempfile
import unittest

path = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "check_reference_obligations.py"
spec = importlib.util.spec_from_file_location("reference_validator", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def sample(root):
    revision = "abc123"
    artifact = root / "capture.txt"
    artifact.write_text("observed", encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    case = {"kind": "positive", "evidence_id": "E-1", "artifact_path": "capture.txt", "artifact_sha256": digest}
    verifier = {"command": "run", "status": "PASS", "revision": revision, "authority": "host", "evidence_id": "E-2", "artifact_path": "capture.txt", "artifact_sha256": digest}
    return {"schema_version": 1, "reference_triggered": True,
            "reference": {"name": "Example", "version": "1", "sha256": digest},
            "candidate_revision": revision, "inventory": ["O-1"],
            "obligations": [{"id": "O-1", "required": True, "status": "PASS",
                             "owner": {"path": "src/main", "revision": revision},
                             "required_cases": ["positive"], "original_cases": [dict(case)],
                             "fixtures": [dict(case)], "required_authority": "host",
                             "verifier": verifier, "contradictions": [], "residual_unknowns": []}]}

class ReferenceValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.data = sample(self.root)

    def validate(self):
        return module.validate(self.data, self.root)

    def test_valid(self):
        self.assertEqual(self.validate(), [])
    def test_missing_evidence_root(self):
        self.assertTrue(module.validate(self.data))
    def test_missing_case(self):
        self.data["obligations"][0]["fixtures"] = []
        self.assertTrue(self.validate())
    def test_static_cannot_prove_host(self):
        self.data["obligations"][0]["verifier"]["authority"] = "static"
        self.assertTrue(self.validate())
    def test_stale_verifier(self):
        self.data["obligations"][0]["verifier"]["revision"] = "old"
        self.assertTrue(self.validate())
    def test_unknown(self):
        self.data["obligations"][0]["residual_unknowns"] = ["missing"]
        self.assertTrue(self.validate())
    def test_duplicate_id(self):
        self.data["obligations"].append(self.data["obligations"][0].copy())
        self.assertTrue(self.validate())
    def test_required_flag_missing(self):
        del self.data["obligations"][0]["required"]
        self.assertTrue(self.validate())
    def test_required_flag_invalid(self):
        self.data["obligations"][0]["required"] = "false"
        self.assertTrue(self.validate())
    def test_duplicate_required_case(self):
        self.data["obligations"][0]["required_cases"] = ["positive", "positive"]
        self.assertTrue(self.validate())
    def test_unknown_authority(self):
        self.data["obligations"][0]["verifier"]["authority"] = "fictional"
        self.assertTrue(self.validate())
    def test_evidence_hash_and_containment(self):
        record = self.data["obligations"][0]["fixtures"][0]
        self.assertTrue(module.evidence_integrity(record, self.root))
        (self.root / "capture.txt").write_text("tampered")
        self.assertFalse(module.evidence_integrity(record, self.root))
        record["artifact_path"] = "../outside.txt"
        self.assertFalse(module.evidence_integrity(record, self.root))
    def test_tampered_fixture_fails_ledger(self):
        (self.root / "capture.txt").write_text("tampered")
        self.assertTrue(self.validate())
    def test_invalid_reference_hash(self):
        self.data["reference"]["sha256"] = "not-a-hash"
        self.assertTrue(self.validate())
    def test_missing_inventory_behavior(self):
        self.data["inventory"].append("O-2")
        self.assertTrue(self.validate())
    def test_uninventoried_obligation(self):
        self.data["inventory"] = ["O-2"]
        self.assertTrue(self.validate())
    def test_not_triggered(self):
        self.assertEqual(module.validate({"schema_version": 1, "reference_triggered": False}), [])

if __name__ == "__main__":
    unittest.main()
