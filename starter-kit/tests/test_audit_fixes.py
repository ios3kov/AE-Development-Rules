"""Run the offline audit regressions in every existing self-test CI job."""
from pathlib import Path
import shutil
import subprocess
import unittest


class AuditFixesTests(unittest.TestCase):
    def test_offline_contracts_and_repository_anchors(self):
        root = Path(__file__).resolve().parents[2]
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required; missing checks cannot pass")
        result = subprocess.run(
            [node, str(root / "starter-kit/tests/audit-fixes.mjs"), "--repository"],
            cwd=root, capture_output=True, text=True, timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
