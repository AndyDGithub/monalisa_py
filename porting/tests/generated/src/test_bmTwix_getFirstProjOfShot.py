"""Auto-generated parity/TDD skeleton for MATLAB port."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import pytest

TARGET_FILE = Path(__file__).resolve().parents[4] / "src/twix/bmTwix_getFirstProjOfShot.py"


def _load_target_function():
    spec = spec_from_file_location("ported_module", TARGET_FILE)
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return getattr(module, 'bmTwix_getFirstProjOfShot')


def test_signature_smoke():
    # Smoke test only: importability and callable signature exposure.
    fn = _load_target_function()
    assert callable(fn)


def test_expected_behavior_contract():
    # Source MATLAB file: twix/bmTwix_getFirstProjOfShot.m
    pytest.skip('Define behavior contract from MATLAB code and downstream callers.')
