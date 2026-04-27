"""Unit tests for volume element / Voronoi computation."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.geom1.bmVolumeElement1 import bmVolumeElement1
from src.geom123.bmVolumeElement import bmVolumeElement


def _phyllotaxis_traj(nLines=20, nPt_per_line=16):
    """Return a (3, N_n, nLines) phyllotaxis trajectory."""
    from src.traj3.bmTraj_fullRadial3_phyllotaxis_lineAssym2 import (
        bmTraj_fullRadial3_phyllotaxis_lineAssym2,
    )
    N_n = nPt_per_line
    nSeg = 2        # 2 segments; flagSelfNav=True removes SI projection → 1 active
    nShot = nLines + 2   # +2 so that nShot_off=2 leaves nLines active spokes
    nShot_off = 2
    FoV = 0.24
    dK_n = 1.0 / FoV / N_n
    arg = (N_n, nSeg, nShot, dK_n, True, nShot_off)
    return bmTraj_fullRadial3_phyllotaxis_lineAssym2(arg)


class TestBmVolumeElement1:
    def test_output_shape(self):
        """bmVolumeElement1 returns shape (nPt, nLine) — (20, 1) for 20-point input."""
        # Input (1, 20): shape[0]==1 triggers internal ravel+reshape to (20, 1)
        t1d = np.linspace(-0.4, 0.4, 20)[np.newaxis, :]
        v = bmVolumeElement1(t1d)
        assert v.shape == (20, 1)

    def test_all_positive(self):
        """Volume elements must be strictly positive."""
        t1d = np.linspace(-0.4, 0.4, 20)[np.newaxis, :]
        v = bmVolumeElement1(t1d)
        assert np.all(v > 0)

    def test_symmetric_traj_symmetric_ve(self):
        """Symmetric trajectory gives symmetric volume elements."""
        t1d = np.linspace(-0.4, 0.4, 21)[np.newaxis, :]
        v = bmVolumeElement1(t1d)
        v_flat = v.ravel()
        np.testing.assert_allclose(v_flat, v_flat[::-1], rtol=1e-5)

    def test_uniform_spacing_constant_ve(self):
        """Uniformly spaced 1-D trajectory → all interior VEs equal."""
        t1d = np.linspace(-0.5, 0.5, 100)[np.newaxis, :]
        v = bmVolumeElement1(t1d)
        # All interior VEs should be equal (uniform spacing)
        np.testing.assert_allclose(v.ravel()[1:-1], v.ravel()[1], rtol=1e-6)

    def test_column_input(self):
        """Column-vector input (nPt, 1) gives same result as row input (1, nPt)."""
        pts = np.linspace(-0.3, 0.3, 15)
        v_row = bmVolumeElement1(pts[np.newaxis, :])   # (1, 15)
        v_col = bmVolumeElement1(pts[:, np.newaxis])   # (15, 1)
        np.testing.assert_allclose(v_row, v_col, rtol=1e-10)


class TestBmVolumeElement3D:
    @pytest.mark.slow
    def test_voronoi_output_shape(self):
        """bmVolumeElement with voronoi_full_radial3 returns (1, nPt)."""
        t = _phyllotaxis_traj(15, 8)
        v = bmVolumeElement(t, 'voronoi_full_radial3')
        nPt = t.shape[1] * t.shape[2]
        assert v.shape == (1, nPt)

    @pytest.mark.slow
    def test_voronoi_all_positive(self):
        """Voronoi volume elements are strictly positive."""
        t = _phyllotaxis_traj(15, 8)
        v = bmVolumeElement(t, 'voronoi_full_radial3')
        assert np.all(v > 0)

    @pytest.mark.slow
    def test_voronoi_sum_bounded(self):
        """Sum of Voronoi VEs is bounded (roughly 1 for normalised trajectory)."""
        t = _phyllotaxis_traj(20, 16)
        v = bmVolumeElement(t, 'voronoi_full_radial3')
        total = float(np.sum(v))
        assert 0 < total < 1e6, f"Unexpected Voronoi sum: {total}"
