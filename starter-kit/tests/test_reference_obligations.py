import importlib.util
import pathlib
import tempfile
import hashlib
import unittest

path = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "check_reference_obligations.py"
spec = importlib.util.spec_from_file_location("reference_validator", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def sample():
    rev = "abc123"
    case = {"kind": "positive", "evidence_id": "E-1", "artifact_sha256": "hash"}
    return {"schema_version": 1, "reference_triggered": True, "reference": {"name": "Example", "version": "1", "sha256": "hash"}, "candidate_revision": rev, "obligations": [{"id": "O-1", "required": True, "status": "PASS", "owner": {"path": "src/main", "revision": rev}, "required_cases": ["positive"], "original_cases": [case], "fixtures": [case], "required_authority": "host", "verifier": {"command": "run", "status": "PASS", "revision": rev, "authority": "host", "evidence_id": "E-2", "artifact_sha256": "hash"}, "contradictions": [], "residual_unknowns": []}]}

class ReferenceValidatorTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(module.validate(sample()), [])
    def test_missing_case(self):
        x = sample(); x["obligations"][0]["fixtures"] = []
        self.assertTrue(module.validate(x))
    def test_static_cannot_prove_host(self):
        x = sample(); x["obligations"][0]["verifier"]["authority"] = "static"
        self.assertTrue(module.validate(x))
    def test_stale_verifier(self):
        x = sample(); x["obligations"][0]["verifier"]["revision"] = "old"
        self.assertTrue(module.validate(x))
    def test_unknown(self):
        x = sample(); x["obligations"][0]["residual_unknowns"] = ["missing"]
        self.assertTrue(module.validate(x))
    def test_duplicate_id(self):
        x = sample(); x["obligations"].append(x["obligations"][0].copy())
        self.assertTrue(module.validate(x))
    def test_required_flag_missing(self):
        x = sample(); del x["obligations"][0]["required"]
        self.assertTrue(module.validate(x))
    def test_required_flag_invalid(self):
        x = sample(); x["obligations"][0]["required"] = "false"
        self.assertTrue(module.validate(x))
    def test_duplicate_required_case(self):
        x = sample(); x['obligations'][0]['required_cases'] = ['positive', 'positive']
        self.assertTrue(module.validate(x))
    def test_unknown_authority(self):
        x = sample(); x['obligations'][0]['verifier']['authority'] = 'fictional'
        self.assertTrue(module.validate(x))
    def test_evidence_hash_and_containment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            file = root / "capture.txt"
            file.write_text("observed")
            record = {"artifact_path": "capture.txt", "artifact_sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
            self.assertTrue(module.evidence_integrity(record, root))
            file.write_text("tampered")
            self.assertFalse(module.evidence_integrity(record, root))
            record["artifact_path"] = "../outside.txt"
            self.assertFalse(module.evidence_integrity(record, root))
    def test_not_triggered(self):
        x = {"schema_version": 1, "reference_triggered": False}
        self.assertEqual(module.validate(x), [])

if __name__ == "__main__":
    unittest.main()
