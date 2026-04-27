"""Unit tests for bmGridder_n2u_leight."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gridding123.m.bmGridder_n2u_leight import bmGridder_n2u_leight


def _cartesian_traj(N=8, FoV=0.24):
    """Dense Cartesian trajectory; every grid point sampled once."""
    dK = 1.0 / FoV
    spacing = dK / N
    ax = (np.arange(N) - N // 2) * spacing
    x, y, z = np.meshgrid(ax, ax, ax, indexing='ij')
    t = np.vstack([x.ravel(), y.ravel(), z.ravel()])   # (3, N^3)
    return t


def _radial_traj(nLines=20, nPt_per_line=8):
    rng = np.random.default_rng(3)
    angles = rng.uniform(0, np.pi, (nLines, 2))
    r = np.linspace(-0.4, 0.4, nPt_per_line)
    pts = []
    for theta, phi in angles:
        d = np.array([np.sin(theta) * np.cos(phi),
                      np.sin(theta) * np.sin(phi),
                      np.cos(theta)])
        pts.append(np.outer(d, r))
    return np.concatenate(pts, axis=1)


def test_output_shape_single_channel():
    """Returns (2, Nx, Ny, Nz) for 2-channel input (bmPointReshape treats (1,nPt) as 1D)."""
    N = 8
    N_u = [N, N, N]
    dK_u = np.ones(3) / 0.24
    t = _radial_traj(10, 8)
    nPt = t.shape[1]
    # Use 2 channels: (1, nPt) gets collapsed to 1D by bmPointReshape
    y = np.ones((2, nPt), dtype=np.complex64)
    v = np.ones((1, nPt), dtype=np.float32) * 1e-4

    out = bmGridder_n2u_leight(y, t, v, N_u, dK_u)
    assert out.shape == (2, N, N, N)


def test_output_shape_multi_channel():
    """Returns (nCh, Nx, Ny, Nz) for multi-channel input."""
    N = 8
    nCh = 4
    N_u = [N, N, N]
    dK_u = np.ones(3) / 0.24
    t = _radial_traj(10, 8)
    nPt = t.shape[1]
    y = np.ones((nCh, nPt), dtype=np.complex64)
    v = np.ones((1, nPt), dtype=np.float32) * 1e-4

    out = bmGridder_n2u_leight(y, t, v, N_u, dK_u)
    assert out.shape == (nCh, N, N, N)


def test_output_dtype():
    """Output is complex64."""
    t = _radial_traj(8, 6)
    nPt = t.shape[1]
    y = np.ones((2, nPt), dtype=np.complex64)
    v = np.ones((1, nPt)) * 1e-4
    out = bmGridder_n2u_leight(y, t, v, [8, 8, 8], np.ones(3) / 0.24)
    assert out.dtype == np.complex64


def test_output_finite():
    """No NaN or Inf for well-behaved input."""
    t = _radial_traj(15, 10)
    nPt = t.shape[1]
    y = np.random.randn(2, nPt).astype(np.complex64)
    v = np.ones((1, nPt)) * 1e-4
    out = bmGridder_n2u_leight(y, t, v, [8, 8, 8], np.ones(3) / 0.24)
    assert np.all(np.isfinite(out))


def test_zero_input_gives_zero_output():
    """All-zero data → all-zero gridded output."""
    t = _radial_traj(8, 6)
    nPt = t.shape[1]
    y = np.zeros((2, nPt), dtype=np.complex64)
    v = np.ones((1, nPt)) * 1e-4
    out = bmGridder_n2u_leight(y, t, v, [8, 8, 8], np.ones(3) / 0.24)
    np.testing.assert_array_equal(out, 0)


def test_linearity():
    """Gridder is linear: grid(a*y1 + b*y2) = a*grid(y1) + b*grid(y2)."""
    t = _radial_traj(10, 8)
    nPt = t.shape[1]
    rng = np.random.default_rng(5)
    # Use 2 channels to avoid bmPointReshape collapsing (1, nPt) to 1D
    y1 = (rng.standard_normal((2, nPt)) + 1j * rng.standard_normal((2, nPt))).astype(np.complex64)
    y2 = (rng.standard_normal((2, nPt)) + 1j * rng.standard_normal((2, nPt))).astype(np.complex64)
    v = np.ones((1, nPt), dtype=np.float32) * 1e-4
    a, b = np.float32(2.0), np.float32(-1.5)
    kw = dict(t=t, v=v, N_u=[8, 8, 8], dK_u=np.ones(3) / 0.24)

    out1 = bmGridder_n2u_leight(y1, **kw)
    out2 = bmGridder_n2u_leight(y2, **kw)
    out_comb = bmGridder_n2u_leight((a * y1 + b * y2).astype(np.complex64), **kw)

    np.testing.assert_allclose(out_comb, a * out1 + b * out2, rtol=1e-5, atol=1e-5)


def test_real_input_finite():
    """Real k-space data produces finite output."""
    t = _radial_traj(10, 8)
    nPt = t.shape[1]
    y = np.ones((2, nPt), dtype=np.float32).astype(np.complex64)
    v = np.ones((1, nPt), dtype=np.float32) * 1e-4
    out = bmGridder_n2u_leight(y, t, v, [8, 8, 8], np.ones(3) / 0.24)
    assert out.shape == (2, 8, 8, 8)
    assert np.all(np.isfinite(out))


def test_multichannel_independence():
    """Each pair of channels is gridded independently (avoids (1,nPt) collapse)."""
    t = _radial_traj(8, 6)
    nPt = t.shape[1]
    rng = np.random.default_rng(6)
    y = (rng.standard_normal((4, nPt)) + 1j * rng.standard_normal((4, nPt))).astype(np.complex64)
    v = np.ones((1, nPt)) * 1e-4
    kw = dict(t=t, v=v, N_u=[8, 8, 8], dK_u=np.ones(3) / 0.24)

    out_all = bmGridder_n2u_leight(y, **kw)
    # Compare first 2 channels gridded together vs gridding all 4
    out_02 = bmGridder_n2u_leight(y[[0, 2]], **kw)
    np.testing.assert_allclose(out_all[[0, 2]], out_02, rtol=1e-6, atol=1e-6)
