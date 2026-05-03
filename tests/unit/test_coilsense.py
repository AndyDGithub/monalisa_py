"""Unit tests for coil sensitivity modules (bmCoilSense_nonCart_*)."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def _radial_traj(nLines=10, nPt_per_line=8):
    rng = np.random.default_rng(11)
    angles = rng.uniform(0, np.pi, (nLines, 2))
    r = np.linspace(-0.4, 0.4, nPt_per_line)
    pts = []
    for theta, phi in angles:
        d = np.array([np.sin(theta) * np.cos(phi),
                      np.sin(theta) * np.sin(phi),
                      np.cos(theta)])
        pts.append(np.outer(d, r))
    return np.concatenate(pts, axis=1)


def _build_gn(N_u=None, nLines=10, nPt_per_line=8):
    from src.gridding123.m.bmTraj2SparseMat import bmTraj2SparseMat
    if N_u is None:
        N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.24
    t = _radial_traj(nLines, nPt_per_line)
    nPt = t.shape[1]
    v = np.ones((1, nPt)) * 1e-4
    Gn, Gu, Gut = bmTraj2SparseMat(t, v, N_u, dK_u)
    return Gn, t, v


class TestBmCoilSenseNonCartMaskAutomatic:
    def test_output_shape(self):
        """Returns a mask with shape (Nu_tot,) or (Nx, Ny, Nz)."""
        from src.coilSense.nonCart.bmCoilSense_nonCart_mask_automatic import (
            bmCoilSense_nonCart_mask_automatic,
        )
        N_u = np.array([8, 8, 8])
        Gn, t, v = _build_gn(N_u)
        nPt = t.shape[1]
        rng = np.random.default_rng(12)
        y = (rng.standard_normal((nPt, 1)) + 1j * rng.standard_normal((nPt, 1))).astype(np.complex64)
        mask = bmCoilSense_nonCart_mask_automatic(y, Gn, True)
        Nu_tot = int(np.prod(N_u))
        assert mask.size == Nu_tot

    def test_output_bool(self):
        """Mask contains boolean or integer values in {0, 1}."""
        from src.coilSense.nonCart.bmCoilSense_nonCart_mask_automatic import (
            bmCoilSense_nonCart_mask_automatic,
        )
        N_u = np.array([8, 8, 8])
        Gn, t, v = _build_gn(N_u)
        nPt = t.shape[1]
        y = np.ones((nPt, 1), dtype=np.complex64)
        mask = bmCoilSense_nonCart_mask_automatic(y, Gn, True)
        unique_vals = np.unique(mask.astype(int))
        assert set(unique_vals).issubset({0, 1})


class TestBmNasha:
    """Functional tests for bmNasha via Gn."""

    def test_output_block_format(self):
        """bmNasha returns (Nx, Ny, Nz, nCh) for 1-D y input."""
        from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
        N_u = np.array([8, 8, 8])
        Gn, t, v = _build_gn(N_u)
        nPt = t.shape[1]
        y = np.ones(nPt, dtype=np.complex64)   # 1-D → treated as (nPt, 1)
        x = bmNasha(y, Gn, N_u)
        assert x.shape == (8, 8, 8, 1)

    def test_multichannel_output(self):
        """bmNasha returns (Nx, Ny, Nz, nCh) for multi-channel input."""
        from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
        N_u = np.array([8, 8, 8])
        Gn, t, v = _build_gn(N_u)
        nPt = t.shape[1]
        nCh = 3
        rng = np.random.default_rng(0)
        y = (rng.standard_normal((nPt, nCh)) + 1j * rng.standard_normal((nPt, nCh))).astype(np.complex64)
        x = bmNasha(y, Gn, N_u)
        assert x.shape == (8, 8, 8, nCh)

    def test_complex_output(self):
        """bmNasha output is complex."""
        from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
        N_u = np.array([8, 8, 8])
        Gn, t, v = _build_gn(N_u)
        nPt = t.shape[1]
        y = np.ones(nPt, dtype=np.complex64)
        x = bmNasha(y, Gn, N_u)
        assert np.iscomplexobj(x)

    def test_zero_input(self):
        """All-zero input → all-zero output."""
        from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
        N_u = np.array([8, 8, 8])
        Gn, t, v = _build_gn(N_u)
        nPt = t.shape[1]
        y = np.zeros(nPt, dtype=np.complex64)
        x = bmNasha(y, Gn, N_u)
        np.testing.assert_allclose(np.abs(x), 0, atol=1e-6)

    def test_finite_output(self):
        """No NaN or Inf for well-behaved input."""
        from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
        N_u = np.array([8, 8, 8])
        Gn, t, v = _build_gn(N_u)
        nPt = t.shape[1]
        rng = np.random.default_rng(1)
        y = (rng.standard_normal(nPt) + 1j * rng.standard_normal(nPt)).astype(np.complex64)
        x = bmNasha(y, Gn, N_u)
        assert np.all(np.isfinite(x))


class TestBmSparseMat:
    """Tests for bmSparseMatScipy class."""

    def test_attributes(self):
        """Gn has the required bmSparseMat-compatible attributes."""
        N_u = np.array([8, 8, 8])
        Gn, _, _ = _build_gn(N_u)
        assert hasattr(Gn, 'N_u')
        assert hasattr(Gn, 'd_u')
        assert hasattr(Gn, 'r_size')
        assert hasattr(Gn, 'matrix')
        assert hasattr(Gn, 'kernel_type')
        assert hasattr(Gn, 'nWin')

    def test_N_u_matches(self):
        """Gn.N_u matches the grid size used at construction."""
        N_u = np.array([8, 8, 8])
        Gn, _, _ = _build_gn(N_u)
        np.testing.assert_array_almost_equal(Gn.N_u[:3], N_u.astype(np.float64))

    def test_r_size_is_nPt(self):
        """Gn.r_size equals the number of k-space samples."""
        N_u = np.array([8, 8, 8])
        nLines, nPt_per_line = 10, 8
        Gn, t, _ = _build_gn(N_u, nLines, nPt_per_line)
        assert int(Gn.r_size) == t.shape[1]

    def test_matrix_shape(self):
        """Gn.matrix has shape (Nu_tot, nPt)."""
        N_u = np.array([8, 8, 8])
        nLines, nPt_per_line = 10, 8
        Gn, t, _ = _build_gn(N_u, nLines, nPt_per_line)
        Nu_tot = int(np.prod(N_u))
        nPt = t.shape[1]
        assert Gn.matrix.shape == (Nu_tot, nPt)
