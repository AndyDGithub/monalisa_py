"""Auto-generated structural contract test (MATLAB -> Python)."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import inspect


TARGET_FILE = Path(__file__).resolve().parents[3] / "src/mex/m/compile_mex_for_monalisa.py"
EXPECTED_FUNCTION_NAME = "a"
EXPECTED_ARG_COUNT = 0


def _load_module():
    spec = spec_from_file_location("ported_module", TARGET_FILE)
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_module_importable():
    module = _load_module()
    assert module is not None


def test_expected_function_exists():
    module = _load_module()
    assert hasattr(module, EXPECTED_FUNCTION_NAME)
    fn = getattr(module, EXPECTED_FUNCTION_NAME)
    assert callable(fn)


def test_positional_arity_matches_matlab():
    module = _load_module()
    fn = getattr(module, EXPECTED_FUNCTION_NAME)
    sig = inspect.signature(fn)
    positional = [
        p
        for p in sig.parameters.values()
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    assert len(positional) == EXPECTED_ARG_COUNT


def test_not_fallback_stub():
    text = TARGET_FILE.read_text(encoding="utf-8", errors="ignore")
    assert "Fallback stub generated because automatic translation did not compile yet" not in text
    assert "# compile_error:" not in text
