#!/usr/bin/env python3
"""Compatibility entry point for the optional agent-evaluation package."""
import importlib.util
from pathlib import Path
import sys

_path = Path(__file__).resolve().parents[2] / 'packages/agent-evaluation/agent_evaluation.py'
_spec = importlib.util.spec_from_file_location(__name__, _path)
_module = importlib.util.module_from_spec(_spec)
sys.modules[__name__] = _module
_spec.loader.exec_module(_module)
if __name__ == '__main__':
    sys.exit(_module.main())
