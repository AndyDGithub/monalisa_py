"""
Parity execution test for trajectory and volume element computation.

Tests that the Python-computed k-space trajectory and volume elements
numerically match the MATLAB reference stored in:
  monalisa/demo/data_demo/data_8_tutorial_1/results/mitosius_allLines/cell_1_1/

The MATLAB-recorded SHA-256 fingerprints (fingerprints.json) serve as ground
truth for size and dtype; approximate comparison (allclose) is used for values
because sin/cos implementations differ by 1 ULP between MATLAB and NumPy.

Volume element tests are marked `slow` and are skipped unless
MONALISA_SLOW_TESTS=1 is set (Voronoi on 42 k lines takes several minutes).
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pathlib import Path
import numpy as np
import pytest

from tests.parity import load_parity_data, matlab_fingerprint

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_MONALISA_PY_ROOT = Path(__file__).parents[2]
_MONALISA_ROOT    = _MONALISA_PY_ROOT.parent / "monalisa"
_DATA_DIR         = _MONALISA_ROOT / "demo" / "data_demo" / "data_8_tutorial_1"
_BRAIN_SCAN       = _DATA_DIR / "brainScan.dat"
_MATLAB_T_MAT     = _DATA_DIR / "results" / "mitosius_allLines" / "cell_1_1" / "t.mat"
_MATLAB_VE_MAT    = _DATA_DIR / "results" / "mitosius_allLines" / "cell_1_1" / "ve.mat"

_SLOW = os.environ.get("MONALISA_SLOW_TESTS", "0") == "1"

pytestmark = pytest.mark.skipif(
    not _BRAIN_SCAN.exists(),
    reason=f"brainScan.dat not found at {_BRAIN_SCAN}",
)


def _load_matlab_array(mat_path):
    """Load a 64-bit floating-point array from a MATLAB v7.3 HDF5 .mat file."""
    import mat73
    mat = mat73.loadmat(str(mat_path))
    key = [k for k in mat.keys() if not k.startswith("_")][0]
    return mat[key]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def acq_params():
    from src.rawDataReader.createRawDataReader import createRawDataReader
    reader = createRawDataReader(str(_BRAIN_SCAN), False)
    p = reader.acquisitionParams
    p.traj_type = "full_radial3_phylotaxis"
    return p


@pytest.fixture(scope="module")
def t_tot(acq_params):
    from src.traj3.bmTraj_fullRadial3_phyllotaxis_lineAssym2 import (
        bmTraj_fullRadial3_phyllotaxis_lineAssym2,
    )
    return bmTraj_fullRadial3_phyllotaxis_lineAssym2(acq_params)


@pytest.fixture(scope="module")
def t_matlab():
    if not _MATLAB_T_MAT.exists():
        pytest.skip(f"MATLAB t.mat not found at {_MATLAB_T_MAT}")
    return _load_matlab_array(_MATLAB_T_MAT)


@pytest.fixture(scope="module")
def ve_matlab():
    if not _MATLAB_VE_MAT.exists():
        pytest.skip(f"MATLAB ve.mat not found at {_MATLAB_VE_MAT}")
    return _load_matlab_array(_MATLAB_VE_MAT)


# ---------------------------------------------------------------------------
# Trajectory tests  (fast)
# ---------------------------------------------------------------------------

class TestTrajectory:

    def test_shape(self, t_tot):
        assert t_tot.shape == (3, 480, 42630), (
            f"Expected (3, 480, 42630), got {t_tot.shape}"
        )

    def test_dtype(self, t_tot):
        assert t_tot.dtype == np.float64

    def test_values_allclose_matlab(self, t_tot, t_matlab):
        """Python trajectory values must match MATLAB to ~1e-12 relative tolerance."""
        t_ref = np.asarray(t_matlab, dtype=np.float64)
        assert t_tot.shape == t_ref.shape, (
            f"Shape mismatch: Python {t_tot.shape} vs MATLAB {t_ref.shape}"
        )
        max_abs = float(np.max(np.abs(t_tot - t_ref)))
        assert np.allclose(t_tot, t_ref, rtol=1e-12, atol=1e-13), (
            f"Trajectory values differ: max_abs_diff={max_abs:.3e}"
        )

    def test_fingerprint_info(self, t_tot):
        """Report the fingerprint — expected NOT to match due to 1-ULP sin/cos diffs."""
        fp = matlab_fingerprint(t_tot, "double", False)
        expected = "43669ad68af48ee1d6130e018ac5b83b82e337f3bd6e85d5e93b5f5e36122652"
        # Exact match is not required (1-ULP sin/cos differences between
        # MATLAB's math library and NumPy's cause different last bits).
        # This test documents the known fingerprint discrepancy.
        if fp != expected:
            pytest.xfail(
                f"Trajectory fingerprint differs by <1 ULP in sin/cos.\n"
                f"  got:      {fp}\n"
                f"  expected: {expected}"
            )

    def test_no_nans(self, t_tot):
        assert not np.any(np.isnan(t_tot)), "Trajectory contains NaN values"

    def test_no_infs(self, t_tot):
        assert not np.any(np.isinf(t_tot)), "Trajectory contains Inf values"

    def test_range(self, t_tot):
        # With N=480, FoV=240, scale=N/FoV=2; r in [-0.5, 0.5-1/N]: values in ~[-1, 1]
        assert np.max(np.abs(t_tot)) < 1.1, (
            f"Trajectory values unexpectedly large: max={np.max(np.abs(t_tot)):.3f}"
        )

    def test_radii_at_endpoints(self, t_tot):
        # The L2 norm at the last radial sample should be close to (0.5 - 1/N)*N/FoV * 1
        norms_last = np.sqrt(np.sum(t_tot[:, -1, :] ** 2, axis=0))
        expected_max_r = (0.5 - 1.0 / 480) * 2.0  # N_n*dK_n = 480/240 = 2
        assert np.allclose(norms_last, expected_max_r, atol=2e-10), (
            f"Endpoint norms not close to {expected_max_r:.6f}: "
            f"max dev = {np.max(np.abs(norms_last - expected_max_r)):.3e}"
        )


# ---------------------------------------------------------------------------
# Volume element tests  (slow — require MONALISA_SLOW_TESTS=1)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _SLOW, reason="Set MONALISA_SLOW_TESTS=1 to run slow Voronoi tests")
class TestVolumeElements:

    @pytest.fixture(scope="class")
    def ve_tot(self, t_tot):
        from src.geom123.bmVolumeElement import bmVolumeElement
        return bmVolumeElement(t_tot, "voronoi_full_radial3")

    def test_shape(self, ve_tot, t_tot):
        expected_len = t_tot.shape[1] * t_tot.shape[2]
        assert ve_tot.shape == (1, expected_len), (
            f"Expected (1, {expected_len}), got {ve_tot.shape}"
        )

    def test_dtype(self, ve_tot):
        assert ve_tot.dtype == np.float64

    def test_positive(self, ve_tot):
        assert np.all(ve_tot > 0), (
            f"Volume elements contain non-positive values: "
            f"min={np.min(ve_tot):.3e}"
        )

    def test_no_nans(self, ve_tot):
        assert not np.any(np.isnan(ve_tot)), "Volume elements contain NaN"

    def test_values_allclose_matlab(self, ve_tot, ve_matlab):
        ve_ref = np.asarray(ve_matlab, dtype=np.float64).ravel()
        ve_py  = ve_tot.ravel()
        assert ve_py.shape == ve_ref.shape, (
            f"Shape mismatch: Python {ve_py.shape} vs MATLAB {ve_ref.shape}"
        )
        assert np.allclose(ve_py, ve_ref, rtol=1e-6, atol=0), (
            f"Volume elements differ: max rel diff = "
            f"{np.max(np.abs(ve_py - ve_ref) / (np.abs(ve_ref) + 1e-30)):.3e}"
        )

    def test_fingerprint(self, ve_tot):
        fp = matlab_fingerprint(ve_tot, "double", False)
        expected = "f2a94ed3dff8ed9affd15c7c43817577617b1444c9bec800617c628110d81805"
        assert fp == expected, (
            f"Volume element fingerprint mismatch:\n"
            f"  got:      {fp}\n"
            f"  expected: {expected}"
        )


# ---------------------------------------------------------------------------
# Full Mathilda pipeline — x_tot  (slowest; requires MONALISA_SLOW_TESTS=1)
# ---------------------------------------------------------------------------

_COIL_SENSE_MAT = _DATA_DIR / "results" / "coil_sensitivity_map.mat"

@pytest.mark.skipif(not _SLOW, reason="Set MONALISA_SLOW_TESTS=1 to run slow Mathilda tests")
@pytest.mark.skipif(
    not _COIL_SENSE_MAT.exists(),
    reason="coil_sensitivity_map.mat not found; run coilSensitivityEstimation_script first",
)
class TestXTot:
    """
    Run the full bmMathilda pipeline on the tutorial data and compare
    the output x_tot against the MATLAB parity reference.

    This test takes ~3-5 minutes on a workstation (20 M k-space points).
    """

    @pytest.fixture(scope="class")
    def x_tot(self, t_tot, acq_params):
        import scipy.io
        from src.geom123.bmVolumeElement import bmVolumeElement
        from src.image123.bmImResize import bmImResize
        from src.fourier123.map_function.nonCartesian.bmMathilda import bmMathilda
        from src.rawDataReader.createRawDataReader import createRawDataReader

        reader = createRawDataReader(str(_BRAIN_SCAN), False)
        p = reader.acquisitionParams
        y_tot = reader.readRawData(True, True)

        ve_tot = bmVolumeElement(t_tot, "voronoi_full_radial3")

        coil_data = scipy.io.loadmat(str(_COIL_SENSE_MAT))
        C = coil_data["C"]

        FoV = p.FoV
        matrix_size = int(FoV / 3)
        N_u = [matrix_size, matrix_size, matrix_size]
        C_resized = bmImResize(C, [48, 48, 48], N_u)

        dK_u = [1.0 / 384, 1.0 / 384, 1.0 / 384]
        x = bmMathilda(y_tot, t_tot, ve_tot, C_resized, N_u, N_u, dK_u)
        return x

    @pytest.fixture(scope="class")
    def x_tot_ref(self):
        mat_vars, _ = load_parity_data("mitosius", "prepared_data")
        return np.asarray(mat_vars["x_tot"], dtype=np.complex64)

    def test_shape(self, x_tot):
        assert x_tot.shape == (80, 80, 80), f"Expected (80,80,80), got {x_tot.shape}"

    def test_dtype_complex(self, x_tot):
        assert np.iscomplexobj(x_tot), f"x_tot must be complex, got {x_tot.dtype}"

    def test_no_nans(self, x_tot):
        assert not np.any(np.isnan(x_tot)), "x_tot contains NaN values"

    def test_values_allclose_matlab(self, x_tot, x_tot_ref):
        """x_tot values must match the MATLAB reference to within relative tolerance."""
        scale = float(np.max(np.abs(x_tot_ref)))
        assert np.allclose(x_tot, x_tot_ref, rtol=1e-3, atol=1e-6 * scale), (
            f"x_tot deviates from MATLAB reference: "
            f"max abs diff = {np.max(np.abs(x_tot - x_tot_ref)):.3e}, "
            f"relative = {np.max(np.abs(x_tot - x_tot_ref)) / scale:.3e}"
        )

    def test_fingerprint(self, x_tot):
        """Exact fingerprint match — may xfail due to float32 rounding differences."""
        fp = matlab_fingerprint(np.asarray(x_tot, dtype=np.complex64), "single", True)
        expected = "a62b0d513877f39c0d474f21ef777a21c5f349966ba3a6afe0e1c30150a26c7b"
        if fp != expected:
            pytest.xfail(
                f"x_tot fingerprint differs (float32 accumulation differences expected).\n"
                f"  got:      {fp}\n"
                f"  expected: {expected}"
            )
