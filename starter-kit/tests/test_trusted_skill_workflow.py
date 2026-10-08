"""Exercise the actual pre-checkout shell guard with adversarial dispatch data."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

WORKFLOW = Path(__file__).resolve().parents[2] / '.github/workflows/trusted-reference-evidence.yml'


def supported_bash():
    # Windows may resolve a WSL stub named bash without an installed distro.
    # Probe execution and also discover Git Bash relative to the actual Git.
    candidates = [shutil.which('bash')]
    git = shutil.which('git')
    if git:
        directory = Path(git).resolve().parent
        candidates.extend([str(directory / 'bash.exe'), str(directory.parent / 'bin/bash.exe')])
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            probe = subprocess.run([candidate, '-c', 'set -euo pipefail; [[ abc =~ ^[a-z]+$ ]]; printf BASH_GUARD_READY'],
                                   capture_output=True, timeout=5)
            if probe.returncode == 0 and probe.stdout == b'BASH_GUARD_READY':
                return candidate
        except (OSError, subprocess.TimeoutExpired):
            continue
    return None


BASH = supported_bash()


class WorkflowInputs(unittest.TestCase):
    def setUp(self):
        self.body = WORKFLOW.read_text()
        block = self.body.split('      - name: Validate public inputs before checkout', 1)[1].split('      - name:', 1)[0]
        self.guard = '\n'.join(line[10:] for line in block.split('        run: |\n', 1)[1].splitlines())
        self.environment = {**os.environ, 'CANDIDATE_SHA': 'a' * 40, 'SOURCE_COMMIT': 'b' * 40,
                            'EVIDENCE_SHA': 'c' * 40,
                            'LEDGER_PATH': 'Evidence/ledger.json', 'SKILL_PATH': 'skills/owned-skill', 'REVIEW_MODE': 'skills'}

    def check(self, **changes):
        if BASH is None:
            self.skipTest('NOT_RUN: executable Bash workflow runtime unavailable')
        return subprocess.run([BASH, '-c', self.guard], env={**self.environment, **changes},
                              capture_output=True, timeout=5).returncode

    def test_reference_backwards_compatibility_and_skill_subject(self):
        self.assertEqual(self.check(), 0)
        self.assertEqual(self.check(REVIEW_MODE='reference'), 0)
        self.assertEqual(self.check(REVIEW_MODE=''), 0)
        self.assertNotEqual(self.check(REVIEW_MODE='unknown'), 0)
        self.assertNotEqual(self.check(REVIEW_MODE='reference', LEDGER_PATH=''), 0)

    def test_paths_cannot_escape_or_inject_shell(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'never-created'
            for path in ['../secret', '/tmp/secret', 'x/../../secret', 'a//b', './a', 'a/', 'a\\b',
                         "a; touch '" + str(target) + "'", '$(touch ' + str(target) + ')', '`touch ' + str(target) + '`']:
                self.assertNotEqual(self.check(SKILL_PATH=path), 0, path)
            self.assertFalse(target.exists())

    def test_subject_sha_and_source_pin_are_required_before_checkout(self):
        for sha in ['', 'main', 'a' * 39, 'a' * 41, 'A' * 40, '${{ secrets.X }}', 'a' * 40 + ';false']:
            self.assertNotEqual(self.check(CANDIDATE_SHA=sha), 0)
            self.assertNotEqual(self.check(SOURCE_COMMIT=sha), 0)

    def test_candidate_is_data_and_verifier_has_external_policy_pin(self):
        # Provenance guard prevents editing tested candidate bytes from selecting its own checker.
        self.assertIn("if: github.ref == 'refs/heads/main'", self.body)
        self.assertIn('ref: ${{ github.sha }}', self.body)
        self.assertIn('python3 trusted/starter-kit/scripts/agent_skills.py check', self.body)
        self.assertIn('--candidate-root candidate', self.body)
        self.assertIn('--expected-policy-sha256 "$TRUSTED_SKILL_POLICY_SHA256"', self.body)
        self.assertNotRegex(self.body, r'(?:python\S*|node|bash)\s+candidate/')
        self.assertIn('submodules: false', self.body)
        self.assertIn('lfs: false', self.body)
        self.assertIn('permissions:\n  contents: read', self.body)
        self.assertNotIn('pull_request_target', self.body)


if __name__ == '__main__':
    unittest.main()
