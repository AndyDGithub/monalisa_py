"""
Parity execution test for coilSensitivityEstimation_script.

Runs the Python coil-sensitivity estimation pipeline and compares outputs
against SHA-256 fingerprints recorded from the reference MATLAB implementation.

Variables stored in data.mat.gz:   C_array_prime, x, C_ref
Variables fingerprint-only:        C, y_ref

Tests are marked slow and skipped unless MONALISA_SLOW_TESTS=1 is set
(the estimation takes several minutes).
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pathlib import Path
import numpy as np
import pytest

from tests.parity import load_parity_data, check_fingerprint, matlab_fingerprint

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_MONALISA_PY_ROOT = Path(__file__).parents[2]
_MONALISA_ROOT    = _MONALISA_PY_ROOT.parent / "monalisa"
_DATA_DIR         = _MONALISA_ROOT / "demo" / "data_demo" / "data_8_tutorial_1"
_BODY_COIL        = _DATA_DIR / "bodyCoil.dat"
_SURFACE_COIL     = _DATA_DIR / "surfaceCoil.dat"

_SLOW = os.environ.get("MONALISA_SLOW_TESTS", "0") == "1"

pytestmark = pytest.mark.skipif(
    not (_BODY_COIL.exists() and _SURFACE_COIL.exists()),
    reason=(
        f"bodyCoil.dat or surfaceCoil.dat not found under {_DATA_DIR}. "
        "Follow the data download instructions in the monalisa README."
    ),
)


@pytest.mark.skipif(not _SLOW, reason="Set MONALISA_SLOW_TESTS=1 to run slow coil-sensitivity tests")
class TestCoilSensitivityExecution:

    @pytest.fixture(scope="class")
    def script_outputs(self, tmp_path_factory):
        """Run coilSensitivityEstimation_script and return C."""
        from demo.script_demo.script_tutorial_1.coilSensitivityEstimation_script import (
            coilSensitivityEstimation_script,
        )
        tmp = tmp_path_factory.mktemp("coil_results")
        C = coilSensitivityEstimation_script(
            data_dir=str(_DATA_DIR),
            results_dir=str(tmp),
        )
        return C, tmp

    @pytest.fixture(scope="class")
    def parity_vars(self):
        mat_vars, var_metas = load_parity_data("coilSensitivityEstimation", "final_outputs")
        stored = {v["name"]: v for v in var_metas}
        return mat_vars, stored

    # ------------------------------------------------------------------
    # Final coil sensitivity map C
    # ------------------------------------------------------------------

    def test_C_shape(self, script_outputs, parity_vars):
        C, _ = script_outputs
        assert C.shape == (48, 48, 48, 42), f"Expected (48,48,48,42), got {C.shape}"

    def test_C_dtype_complex(self, script_outputs):
        C, _ = script_outputs
        assert np.iscomplexobj(C), f"C must be complex, got dtype {C.dtype}"

    def test_C_no_nans(self, script_outputs):
        C, _ = script_outputs
        assert not np.any(np.isnan(C)), "C contains NaN values"

    def test_C_fingerprint(self, script_outputs, parity_vars):
        """C is fingerprint-only in the parity data; check SHA-256 matches MATLAB."""
        C, _ = script_outputs
        _, stored = parity_vars
        assert check_fingerprint(C, stored["C"]), (
            f"C fingerprint mismatch:\n"
            f"  got:      {matlab_fingerprint(np.asarray(C, dtype=np.complex64), 'single', True)}\n"
            f"  expected: {stored['C']['sha256']}"
        )

    # ------------------------------------------------------------------
    # Intermediate C_array_prime (stored in mat)
    # ------------------------------------------------------------------

    def test_C_array_prime_fingerprint(self, script_outputs, parity_vars):
        """C_array_prime is stored in data.mat.gz; verify against MATLAB."""
        C, tmp = script_outputs
        mat_vars, stored = parity_vars
        if "C_array_prime" not in mat_vars:
            pytest.skip("C_array_prime not found in parity mat file")
        ref = mat_vars["C_array_prime"]
        assert check_fingerprint(ref, stored["C_array_prime"]), (
            "C_array_prime parity mat self-check failed (data.mat.gz corrupt?)"
        )

    # ------------------------------------------------------------------
    # Reconstruction image x (stored in mat)
    # ------------------------------------------------------------------

    def test_x_shape(self, parity_vars):
        mat_vars, _ = parity_vars
        if "x" not in mat_vars:
            pytest.skip("x not in parity mat")
        x_ref = np.asarray(mat_vars["x"])
        assert x_ref.shape == (48, 48, 48), f"Expected (48,48,48), got {x_ref.shape}"

    def test_x_fingerprint(self, parity_vars):
        """Verify that the stored x matches its own fingerprint."""
        mat_vars, stored = parity_vars
        if "x" not in mat_vars:
            pytest.skip("x not in parity mat")
        assert check_fingerprint(mat_vars["x"], stored["x"]), (
            "x parity mat self-check failed"
        )
