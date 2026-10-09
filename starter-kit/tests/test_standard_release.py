"""Negative checks for the actual privileged publisher's offline gate functions."""
import ast
import io
from pathlib import Path
import tarfile
import unittest
import zipfile


class StandardReleaseTests(unittest.TestCase):
    workflow_name = 'release-10.0.0.yml'
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[2] / '.github/workflows' / cls.workflow_name
        cls.workflow = path.read_text()
        body = cls.workflow.split("          python3 - <<'PY'\n", 1)[1].rsplit('          PY', 1)[0]
        source = '\n'.join(line[10:] for line in body.splitlines())
        tree = ast.parse(source)
        # Never evaluate publisher top-level statements, environment or API calls.
        functions = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'require', 'verified_jobs', 'verify_archive'}], type_ignores=[])
        cls.functions = {'io': io, 'zipfile': zipfile, 'tarfile': tarfile}
        exec(compile(functions, str(path), 'exec'), cls.functions)
        cls.source = source

    def test_exact_required_jobs_cannot_hide_failure_missing_or_duplicates(self):
        verify = self.functions['verified_jobs']
        names = {'linux', 'mac', 'windows'}
        jobs = [{'name': n, 'status': 'completed', 'conclusion': 'success'} for n in names]
        verify(jobs, names)
        for invalid in [jobs[:-1], jobs + [jobs[0]], jobs + [{'name': 'linux', 'status': 'completed', 'conclusion': 'failure'}]]:
            with self.assertRaises(RuntimeError):
                verify(invalid, names)
        for result in ['failure', 'cancelled', 'skipped', None]:
            with self.assertRaises(RuntimeError):
                verify([{**j, 'conclusion': result} for j in jobs], names)

    def zipped(self, contents, mode=0o644):
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w') as archive:
            for name, data in contents.items():
                info = zipfile.ZipInfo(name)
                info.external_attr = mode << 16
                archive.writestr(info, data)
        return out.getvalue()

    def test_archive_changed_missing_added_or_chmod_bytes_reject(self):
        verify = self.functions['verify_archive']
        expected = {'VERSION': (b'10.0.0\n', 0o644)}
        verify(self.zipped({'src/VERSION': b'10.0.0\n'}), 'zip', expected, 'src/')
        for data in [self.zipped({'src/VERSION': b'9.0.0\n'}), self.zipped({}), self.zipped({'src/VERSION': b'10.0.0\n', 'src/extra': b'x'}), self.zipped({'src/VERSION': b'10.0.0\n'}, 0o755), self.zipped({'../VERSION': b'10.0.0\n'})]:
            with self.assertRaises(RuntimeError):
                verify(data, 'zip', expected, 'src/')

    def test_tar_symlink_cannot_borrow_source_identity(self):
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode='w:gz') as archive:
            info = tarfile.TarInfo('src/VERSION')
            info.type = tarfile.SYMTYPE
            info.linkname = '../VERSION'
            archive.addfile(info)
        with self.assertRaises(RuntimeError):
            self.functions['verify_archive'](out.getvalue(), 'tar.gz', {'VERSION': (b'10.0.0\n', 0o644)}, 'src/')

    def test_publication_is_scoped_after_identity_ci_and_asset_verification(self):
        self.assertIn("if: github.repository == 'ios3kov/AE-Development-Rules' && github.ref == 'refs/heads/main'", self.workflow)
        self.assertIn('persist-credentials: false', self.workflow)
        self.assertIn("'Existing tag points elsewhere; never replace it'", self.source)
        self.assertIn("'Published release is missing assets; do not mutate it'", self.source)
        self.assertLess(self.source.index("require(set(ci) == set(required)"), self.source.index("api('/git/tags',"))
        self.assertLess(self.source.index("'Uploaded asset digest/size mismatch'"), self.source.index("{'draft': False"))
        self.assertNotIn('pull_request_target', self.workflow)


class CorrectionReleaseTests(StandardReleaseTests):
    workflow_name = 'release-10.0.1.yml'


class AutomationCorrectionReleaseTests(StandardReleaseTests):
    workflow_name = 'release-10.0.2.yml'


class CompactReleaseTests(StandardReleaseTests):
    workflow_name = 'release-11.0.0.yml'


class CompactCorrectionReleaseTests(StandardReleaseTests):
    workflow_name = 'release-11.0.1.yml'


class FinalizedBaselineReleaseTests(StandardReleaseTests):
    workflow_name = 'release-11.1.0.yml'


if __name__ == '__main__':
    unittest.main()
