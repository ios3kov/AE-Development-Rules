import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_reference_obligations as module

def sample(root):
    revision = "a" * 40
    artifact = root / "capture.txt"
    artifact.write_text("synthetic observation; not an AE/iPhone run", encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    policy = {"schema_version": 1, "reference_triggered": True, "candidate_revision": revision,
              "reference_sha256": digest, "obligations": [{"id": "O-1", "required": True,
                "required_cases": ["positive", "negative"], "required_authority": "host",
                "requirement_ids": ["PROJECT-PARITY"], "check_id": "PARITY-1"}]}
    common = {"artifact_path": "capture.txt", "artifact_sha256": digest, "authority": "host", "status": "PASS",
              "environment": "synthetic fixture", "command": "fixture probe", "tool_version": "1",
              "observed_at": "2026-01-01T00:00:00Z", "run_id": "run-1"}
    obligation = dict(policy["obligations"][0], status="PASS", owner={"path": "src/main", "revision": revision, "sha256": digest},
                      contradictions=[], residual_unknowns=[])
    for role in ("original_cases", "fixtures"):
        obligation[role] = []
        for kind in obligation["required_cases"]:
            record = dict(common, evidence_id=role + "-" + kind, kind=kind)
            if role == "original_cases":
                record.update(reference_sha256=digest, claim_status="OBSERVED")
            else:
                record.update(revision=revision, authority="unit")
            obligation[role].append(record)
    (root/"src").mkdir(exist_ok=True)
    (root/"src/main").write_bytes(artifact.read_bytes())
    report = {"status":"PASS","revision":revision,"obligation_id":"O-1","check_id":"PARITY-1",
              "requirement_ids":["PROJECT-PARITY"],"authority":"host","environment":"synthetic fixture",
              "case_results":{"positive":"PASS","negative":"PASS"}}
    (root/"verifier.json").write_text(json.dumps(report))
    obligation["verifier"] = dict(common, evidence_id="verifier-1", revision=revision,
                                  check_id="PARITY-1", requirement_ids=["PROJECT-PARITY"])
    obligation["verifier"].update(artifact_path="verifier.json", artifact_sha256=hashlib.sha256((root/"verifier.json").read_bytes()).hexdigest())
    return {"schema_version": 1, "reference_triggered": True,
            "reference": {"name": "Synthetic", "version": "1", "sha256": digest},
            "candidate_revision": revision, "inventory": ["O-1"], "obligations": [obligation]}, policy

class ReferenceValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.data, self.policy = sample(self.root)
        self.item = self.data["obligations"][0]

    def validate(self):
        return module.validate(self.data, self.root, self.policy, "a"*40)

    def test_valid(self):
        self.assertEqual(self.validate(), [])
    def test_no_reference_has_no_extra_obligations(self):
        data = {"schema_version":1,"reference_triggered":False}
        self.assertEqual(module.validate(data, policy=dict(data)), [])
    def test_untrusted_trigger_cannot_disable_policy(self):
        self.data["reference_triggered"] = False
        self.assertTrue(self.validate())
    def test_policy_required(self):
        self.assertTrue(module.validate(self.data, self.root))
    def test_required_minimum_cannot_be_lowered(self):
        for field, value in (("required",False),("required_cases",["positive"]),("required_authority","unit"),
                             ("requirement_ids",[]),("check_id","other")):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["obligations"][0][field] = value
                self.assertTrue(module.validate(data,self.root,self.policy))
    def test_coverage_cannot_be_removed(self):
        self.policy["obligations"].append(dict(self.policy["obligations"][0],id="O-2"))
        self.assertTrue(self.validate())
    def test_reviewed_exclusion(self):
        minimum = self.policy["obligations"][0]
        minimum.update(required=False,exclusion_reason="outside selected feature",decision_ref="owner/decision/1")
        self.item.update(minimum,status="NOT_APPLICABLE")
        self.assertEqual(self.validate(),[])
        self.item["exclusion_reason"] = ""
        self.assertTrue(self.validate())
    def test_missing_case(self):
        self.item["fixtures"].pop()
        self.assertTrue(self.validate())
    def test_duplicate_cases(self):
        self.item["fixtures"].append(dict(self.item["fixtures"][0]))
        self.assertTrue(self.validate())
    def test_authority_is_not_host_device_rank(self):
        for value in ("static","unit","device","fictional",[],{}):
            with self.subTest(value=value):
                self.item["verifier"]["authority"] = value
                self.assertTrue(self.validate())
    def test_static_reference_does_not_prove_host(self):
        self.item["original_cases"][0]["authority"] = "static"
        self.assertTrue(self.validate())
    def test_unobserved_claim(self):
        self.item["original_cases"][0]["claim_status"] = "INFERRED"
        self.assertTrue(self.validate())
    def test_stale_subjects(self):
        for target in (self.item["owner"], self.item["verifier"], self.item["fixtures"][0]):
            with self.subTest(target=target):
                target["revision"] = "b"*40
                self.assertTrue(self.validate())
                target["revision"] = "a"*40
    def test_substituted_reference(self):
        self.data["reference"]["sha256"] = "f"*64
        self.assertTrue(self.validate())
    def test_substituted_original(self):
        self.item["original_cases"][0]["reference_sha256"] = "f"*64
        self.assertTrue(self.validate())
    def test_unknown_and_contradiction_fail(self):
        for field in ("contradictions","residual_unknowns"):
            self.item[field] = ["gap"]
            self.assertTrue(self.validate())
            self.item[field] = []
    def test_missing_execution_metadata(self):
        for field in ("observed_at","environment","run_id","tool_version","command","status"):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                del data["obligations"][0]["verifier"][field]
                self.assertTrue(module.validate(data,self.root,self.policy))
    def test_invalid_and_future_time(self):
        for value in ("yesterday","2026-01-01","2099-01-01T00:00:00Z"):
            self.item["verifier"]["observed_at"] = value
            self.assertTrue(self.validate())
    def test_required_not_pass(self):
        for value in ("FAIL","BLOCKED","NOT_RUN","NOT_APPLICABLE"):
            self.item["status"] = value
            self.assertTrue(self.validate())
    def test_duplicate_obligation_and_evidence_ids(self):
        self.item["verifier"]["evidence_id"] = self.item["fixtures"][0]["evidence_id"]
        self.assertTrue(self.validate())
        self.data["obligations"].append(copy.deepcopy(self.item))
        self.assertTrue(self.validate())
    def test_evidence_missing_tampered_and_escape(self):
        record = self.item["verifier"]
        for path in ("missing", "../capture.txt", str(self.root/"capture.txt"), "./capture.txt", "C:\\capture.txt"):
            with self.subTest(path=path):
                record["artifact_path"] = path
                self.assertTrue(self.validate())
        record["artifact_path"] = "capture.txt"
        (self.root / "capture.txt").write_text("tampered")
        self.assertTrue(self.validate())
    def test_symlink_rejected(self):
        try:
            (self.root/"link").symlink_to(self.root/"capture.txt")
        except OSError:
            self.skipTest("symlinks unavailable")
        self.item["verifier"]["artifact_path"] = "link"
        self.assertTrue(self.validate())
    def test_malformed_inputs_fail_without_crash(self):
        for key, values in (("inventory", [None,{},[{}]]),("obligations",[None,{},[None]]),("reference",[None,[],{}])):
            for value in values:
                with self.subTest(key=key,value=value):
                    data = copy.deepcopy(self.data)
                    data[key] = value
                    self.assertTrue(module.validate(data,self.root,self.policy))
    def test_typed_verifier_cannot_hide_failed_case(self):
        report = module.load_json(self.root/"verifier.json")
        report["case_results"]["negative"] = "FAIL"
        (self.root/"verifier.json").write_text(json.dumps(report))
        self.item["verifier"]["artifact_sha256"] = hashlib.sha256((self.root/"verifier.json").read_bytes()).hexdigest()
        self.assertTrue(self.validate())
    def test_owner_bytes_cannot_be_substituted(self):
        (self.root/"src/main").write_text("other implementation")
        self.assertTrue(self.validate())
    def test_cli_exit_status_and_duplicate_json_keys(self):
        ledger, policy = self.root/"ledger.json", self.root/"policy.json"
        policy.write_text(json.dumps(self.policy))
        ledger.write_text(json.dumps(self.data))
        command = [sys.executable,str(SCRIPTS/"check_reference_obligations.py"),str(ledger),
                   "--policy",str(policy),"--evidence-root",str(self.root)]
        result = subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        self.assertFalse(json.loads(result.stdout)["parity_certified"])
        ledger.write_text('{"schema_version":1,"schema_version":1}')
        result = subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,1,result.stderr+result.stdout)
        self.assertEqual(json.loads(result.stdout)["status"],"FAIL")

if __name__ == "__main__":
    unittest.main()
