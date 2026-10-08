#!/usr/bin/env python3
"""Compile and run original offline native fixture, seeded properties/fuzz and actual regression red/green."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

FIXTURE = Path(__file__).resolve().parents[1] / 'examples/native-core'


def run_examples(compiler=None, sanitizer=False):
    compiler = compiler or shutil.which('clang++') or shutil.which('g++')
    if not compiler or not shutil.which(compiler):
        return {'status': 'BLOCKED', 'scope': 'offline-native-examples', 'reason': 'C++17 compiler unavailable', 'host_status': 'NOT_RUN'}
    sources = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FIXTURE.glob('*')) if p.suffix in {'.cpp', '.hpp'}}
    with tempfile.TemporaryDirectory(prefix='ae-rules-native-') as tmp:
        reports = []
        for original in (False, True):
            binary = Path(tmp) / ('original' if original else 'fixed')
            if sys.platform == 'win32':
                binary = binary.with_suffix('.exe')
            argv = [compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-O1', str(FIXTURE / 'check_native_core.cpp'), '-o', str(binary)]
            if original:
                argv.insert(1, '-DDEMONSTRATE_ORIGINAL_DEFECT=1')
            if sanitizer:
                argv[1:1] = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
            build = subprocess.run(argv, capture_output=True, text=True, timeout=90, shell=False)
            if build.returncode:
                return {'status': 'FAIL', 'scope': 'offline-native-examples', 'reason': 'fixture compilation failed', 'diagnostic': build.stderr[-8000:], 'host_status': 'NOT_RUN'}
            result = subprocess.run([str(binary)] + (['--regression-only'] if original else []), capture_output=True, text=True, timeout=30, shell=False)
            reports.append({'variant': 'original-defect' if original else 'fixed', 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        invalid = subprocess.run([compiler, '-std=c++17', '-c', str(FIXTURE / 'invalid_units.cpp'), '-o', str(Path(tmp) / 'invalid.o')], capture_output=True, text=True, timeout=90, shell=False)
        invalid_units_rejected = invalid.returncode != 0 and 'Seconds' in invalid.stderr and 'FrameCount' in invalid.stderr
        regression_detected = reports[1]['exit_code'] == 1 and reports[1]['stderr'].strip() == 'REGRESSION:x-equals-width'
        success = reports[0]['exit_code'] == 0 and regression_detected and invalid_units_rejected
        version = subprocess.run([compiler, '--version'], capture_output=True, text=True, timeout=10, shell=False)
        return {'status': 'PASS' if success else 'FAIL', 'scope': 'offline-native-examples', 'host_status': 'NOT_RUN',
                'sdk_certified': False, 'source_digests': sources, 'compiler': version.stdout.splitlines()[0] if version.stdout else compiler,
                'sanitizers': sanitizer, 'seed': '0xAEE2026', 'iterations': 20000,
                'regression_detected_original': regression_detected, 'invalid_units_compile_rejected': invalid_units_rejected, 'runs': reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler')
    parser.add_argument('--sanitizers', action='store_true')
    args = parser.parse_args()
    try:
        report = run_examples(args.compiler, args.sanitizers)
    except (OSError, subprocess.TimeoutExpired) as exc:
        report = {'status': 'BLOCKED', 'scope': 'offline-native-examples', 'reason': type(exc).__name__, 'host_status': 'NOT_RUN'}
    print(json.dumps(report))
    return 0 if report['status'] == 'PASS' else 2 if report['status'] == 'BLOCKED' else 1

if __name__ == '__main__':
    sys.exit(main())
