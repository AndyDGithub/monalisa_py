"""Unit tests for bmNasha."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
from src.gridding123.m.bmTraj2SparseMat import bmTraj2SparseMat


def _cartesian_traj_3d(N=8, dK=1.0 / 0.24):
    """Dense Cartesian trajectory on a 3-D grid."""
    ax = np.arange(-N // 2, N // 2) * (1.0 / N / (1.0 / dK))
    x, y, z = np.meshgrid(ax, ax, ax, indexing='ij')
    t = np.vstack([x.ravel(), y.ravel(), z.ravel()])   # (3, N^3)
    return t


def _radial_traj_3d(nLines=15, nPt_per_line=8):
    rng = np.random.default_rng(7)
    angles = rng.uniform(0, np.pi, (nLines, 2))
    r = np.linspace(-0.4, 0.4, nPt_per_line)
    pts = []
    for theta, phi in angles:
        ux = np.sin(theta) * np.cos(phi)
        uy = np.sin(theta) * np.sin(phi)
        uz = np.cos(theta)
        pts.append(np.outer(np.array([ux, uy, uz]), r))
    return np.concatenate(pts, axis=1)


def test_output_shape_single_channel():
    """bmNasha returns (Nx, Ny, Nz, 1) for single-channel data."""
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    t = _radial_traj_3d(10, 8)
    nPt = t.shape[1]
    v = np.ones((1, nPt)) * 1e-4
    y = np.random.randn(nPt).astype(np.complex64)

    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)
    x = bmNasha(y, Gn, N_u)

    assert x.shape == (8, 8, 8, 1)


def test_output_shape_multi_channel():
    """bmNasha returns (Nx, Ny, Nz, nCh) for multi-channel data."""
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    t = _radial_traj_3d(10, 8)
    nPt = t.shape[1]
    nCh = 3
    v = np.ones((1, nPt)) * 1e-4
    y = (np.random.randn(nPt, nCh) + 1j * np.random.randn(nPt, nCh)).astype(np.complex64)

    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)
    x = bmNasha(y, Gn, N_u)

    assert x.shape == (8, 8, 8, nCh)


def test_output_dtype():
    """Output is complex64."""
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    t = _radial_traj_3d(8, 6)
    nPt = t.shape[1]
    v = np.ones((1, nPt)) * 1e-4
    y = np.ones(nPt, dtype=np.complex64)

    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)
    x = bmNasha(y, Gn, N_u)

    assert x.dtype == np.complex64


def test_output_finite():
    """No NaN or Inf in output for well-behaved input."""
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    t = _radial_traj_3d(12, 8)
    nPt = t.shape[1]
    v = np.ones((1, nPt)) * 1e-4
    rng = np.random.default_rng(1)
    y = (rng.standard_normal(nPt) + 1j * rng.standard_normal(nPt)).astype(np.complex64)

    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)
    x = bmNasha(y, Gn, N_u)

    assert np.all(np.isfinite(x)), "Output contains NaN or Inf"


def test_linearity():
    """bmNasha is linear: bmNasha(a*y + b*z) = a*bmNasha(y) + b*bmNasha(z)."""
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    t = _radial_traj_3d(8, 6)
    nPt = t.shape[1]
    v = np.ones((1, nPt)) * 1e-4
    rng = np.random.default_rng(2)
    y1 = (rng.standard_normal(nPt) + 1j * rng.standard_normal(nPt)).astype(np.complex64)
    y2 = (rng.standard_normal(nPt) + 1j * rng.standard_normal(nPt)).astype(np.complex64)
    a, b = 2.0 + 0j, -1.5 + 0.5j

    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)
    x1 = bmNasha(y1, Gn, N_u)
    x2 = bmNasha(y2, Gn, N_u)
    x_combined = bmNasha((a * y1 + b * y2).astype(np.complex64), Gn, N_u)

    np.testing.assert_allclose(x_combined, a * x1 + b * x2, rtol=1e-4, atol=1e-4)


def test_N_u_none_uses_G_N_u():
    """Passing N_u=None or empty uses G.N_u."""
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    t = _radial_traj_3d(8, 6)
    nPt = t.shape[1]
    v = np.ones((1, nPt)) * 1e-4
    y = np.ones(nPt, dtype=np.complex64)

    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)
    x1 = bmNasha(y, Gn, N_u)
    x2 = bmNasha(y, Gn, None)

    np.testing.assert_array_equal(x1, x2)
