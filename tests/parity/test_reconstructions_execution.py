"""
Parity execution test for reconstructions_script.

Runs the Python reconstruction pipeline and compares outputs against SHA-256
fingerprints recorded from the reference MATLAB implementation.

Variables stored in data.mat.gz:   x0, x1, x_sensa, x_cs, N_u, dK_u, nFr
Variables fingerprint-only:        (none in this step)

Prerequisites
-------------
- brainScan.dat must exist in the data directory
- The mitosius_allLines directory must already have been created by
  mitosius_script (or a prior test run with MONALISA_SLOW_TESTS=1)
- The coil_sensitivity_map.mat must already have been created by
  coilSensitivityEstimation_script

Tests are gated behind MONALISA_SLOW_TESTS=1.
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
_MONALISA_PY_ROOT  = Path(__file__).parents[2]
_MONALISA_ROOT     = _MONALISA_PY_ROOT.parent / "monalisa"
_DATA_DIR          = _MONALISA_ROOT / "demo" / "data_demo" / "data_8_tutorial_1"
_RESULTS_DIR       = _DATA_DIR / "results"
_BRAIN_SCAN        = _DATA_DIR / "brainScan.dat"
_COIL_SENSE_MAT    = _RESULTS_DIR / "coil_sensitivity_map.mat"
_MITOSIUS_ALLLINES = _RESULTS_DIR / "mitosius_allLines"

_SLOW = os.environ.get("MONALISA_SLOW_TESTS", "0") == "1"

_data_present = (
    _BRAIN_SCAN.exists()
    and _COIL_SENSE_MAT.exists()
    and (_MITOSIUS_ALLLINES / "mitosius_size.mat").exists()
)

pytestmark = pytest.mark.skipif(
    not _BRAIN_SCAN.exists(),
    reason=f"brainScan.dat not found at {_BRAIN_SCAN}",
)


@pytest.mark.skipif(not _SLOW, reason="Set MONALISA_SLOW_TESTS=1 to run slow reconstruction tests")
class TestReconstructionsExecution:

    @pytest.fixture(scope="class")
    def script_outputs(self):
        """Run reconstructions_script and return (x0, x1, x_sensa, x_cs)."""
        if not _data_present:
            pytest.skip(
                "Reconstruction prerequisites missing: run "
                "coilSensitivityEstimation_script and mitosius_script first."
            )
        from demo.script_demo.script_tutorial_1.reconstructions_script import (
            reconstructions_script,
        )
        return reconstructions_script(
            data_dir=str(_DATA_DIR),
            results_dir=str(_RESULTS_DIR),
        )

    @pytest.fixture(scope="class")
    def parity_vars(self):
        mat_vars, var_metas = load_parity_data("reconstructions", "final_reconstructions")
        stored = {v["name"]: v for v in var_metas}
        return mat_vars, stored

    # ------------------------------------------------------------------
    # x0 – gridded regridding (all-lines, frame 0)
    # ------------------------------------------------------------------

    def test_x0_shape(self, script_outputs):
        x0, _, _, _ = script_outputs
        assert x0.shape == (80, 80, 80), f"Expected (80,80,80), got {x0.shape}"

    def test_x0_dtype_complex(self, script_outputs):
        x0, _, _, _ = script_outputs
        assert np.iscomplexobj(x0), f"x0 must be complex, got {x0.dtype}"

    def test_x0_no_nans(self, script_outputs):
        x0, _, _, _ = script_outputs
        assert not np.any(np.isnan(x0)), "x0 contains NaN values"

    def test_x0_fingerprint(self, script_outputs, parity_vars):
        x0, _, _, _ = script_outputs
        _, stored = parity_vars
        assert check_fingerprint(x0, stored["x0"]), (
            f"x0 fingerprint mismatch:\n"
            f"  got:      {matlab_fingerprint(np.asarray(x0, dtype=np.complex64), 'single', True)}\n"
            f"  expected: {stored['x0']['sha256']}"
        )

    # ------------------------------------------------------------------
    # x1 – gridded frames (sequential, frame 0)
    # ------------------------------------------------------------------

    def test_x1_frame0_shape(self, script_outputs):
        _, x1, _, _ = script_outputs
        assert x1[0].shape == (80, 80, 80), f"Expected (80,80,80), got {x1[0].shape}"

    def test_x1_fingerprint(self, script_outputs, parity_vars):
        _, x1, _, _ = script_outputs
        _, stored = parity_vars
        # MATLAB cell array x1 — fingerprint as cell
        x1_arr = np.empty(len(x1), dtype=object)
        for i, xi in enumerate(x1):
            x1_arr[i] = np.asarray(xi, dtype=np.complex64)
        assert check_fingerprint(x1_arr, stored["x1"]), (
            f"x1 fingerprint mismatch.\n"
            f"  expected: {stored['x1']['sha256']}"
        )

    # ------------------------------------------------------------------
    # x_cs – compressed-sensing reconstruction
    # ------------------------------------------------------------------

    def test_x_cs_shape(self, script_outputs):
        _, _, _, x_cs = script_outputs
        assert x_cs.shape == (80, 80, 80), f"Expected (80,80,80), got {x_cs.shape}"

    def test_x_cs_fingerprint(self, script_outputs, parity_vars):
        _, _, _, x_cs = script_outputs
        _, stored = parity_vars
        assert check_fingerprint(x_cs, stored["x_cs"]), (
            f"x_cs fingerprint mismatch:\n"
            f"  got:      {matlab_fingerprint(np.asarray(x_cs, dtype=np.complex64), 'single', True)}\n"
            f"  expected: {stored['x_cs']['sha256']}"
        )

    # ------------------------------------------------------------------
    # Stored reference consistency check
    # ------------------------------------------------------------------

    def test_parity_stored_vars_self_consistent(self, parity_vars):
        """All variables stored in data.mat.gz must match their own fingerprints."""
        mat_vars, stored = parity_vars
        for name, arr in mat_vars.items():
            if name in stored:
                assert check_fingerprint(arr, stored[name]), (
                    f"Parity self-check failed for {name!r}"
                )
