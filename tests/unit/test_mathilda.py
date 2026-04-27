"""Unit tests for bmMathilda (full reconstruction pipeline)."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.fourier123.map_function.nonCartesian.bmMathilda import bmMathilda


def _radial_traj(nLines=10, nPt_per_line=8):
    rng = np.random.default_rng(9)
    angles = rng.uniform(0, np.pi, (nLines, 2))
    r = np.linspace(-0.4, 0.4, nPt_per_line)
    pts = []
    for theta, phi in angles:
        d = np.array([np.sin(theta) * np.cos(phi),
                      np.sin(theta) * np.sin(phi),
                      np.cos(theta)])
        pts.append(np.outer(d, r))
    return np.concatenate(pts, axis=1)   # (3, nPt)


def _y(rng_or_seed, nCh, nPt, zero=False):
    """Create complex k-space data. nCh must be >= 2 to avoid bmPointReshape collapsing to 1D."""
    assert nCh >= 2, "Use nCh >= 2 to avoid bmPointReshape 1D collapse"
    rng = np.random.default_rng(rng_or_seed) if isinstance(rng_or_seed, int) else rng_or_seed
    if zero:
        return np.zeros((nCh, nPt), dtype=np.complex64)
    return (rng.standard_normal((nCh, nPt)) + 1j * rng.standard_normal((nCh, nPt))).astype(np.complex64)


def test_output_shape_no_coil_sense():
    """Without coil sensitivity, output first 3 dims are (Nx, Ny, Nz)."""
    N_u = [8, 8, 8]
    dK_u = list(np.ones(3) / 0.24)
    t = _radial_traj(8, 6)
    nPt = t.shape[1]
    y = _y(0, 2, nPt)
    v = np.ones((1, nPt), dtype=np.float32) * 1e-4

    x = bmMathilda(y, t, v, None, N_u, N_u, dK_u)
    assert x.shape[:3] == (8, 8, 8)


def test_output_shape_with_coil_sense():
    """With coil sensitivity, output first 3 dims are (Nx, Ny, Nz)."""
    N_u = [8, 8, 8]
    dK_u = list(np.ones(3) / 0.24)
    t = _radial_traj(8, 6)
    nCh = 2
    nPt = t.shape[1]
    rng = np.random.default_rng(0)
    y = _y(rng, nCh, nPt)
    v = np.ones((1, nPt), dtype=np.float32) * 1e-4
    C = (rng.standard_normal((8, 8, 8, nCh)) + 1j * rng.standard_normal((8, 8, 8, nCh))).astype(np.complex64)

    x = bmMathilda(y, t, v, C, N_u, N_u, dK_u)
    assert x.shape[:3] == (8, 8, 8)


def test_output_is_complex():
    """Output is complex."""
    N_u = [8, 8, 8]
    dK_u = list(np.ones(3) / 0.24)
    t = _radial_traj(8, 6)
    nPt = t.shape[1]
    y = _y(1, 2, nPt)
    v = np.ones((1, nPt)) * 1e-4

    x = bmMathilda(y, t, v, None, N_u, N_u, dK_u)
    assert np.iscomplexobj(x)


def test_output_finite():
    """No NaN or Inf in output for well-behaved input."""
    N_u = [8, 8, 8]
    dK_u = list(np.ones(3) / 0.24)
    t = _radial_traj(12, 8)
    nPt = t.shape[1]
    y = _y(4, 2, nPt)
    v = np.ones((1, nPt)) * 1e-4

    x = bmMathilda(y, t, v, None, N_u, N_u, dK_u)
    assert np.all(np.isfinite(x))


def test_zero_input_gives_zero_output():
    """All-zero raw data → near-zero image."""
    N_u = [8, 8, 8]
    dK_u = list(np.ones(3) / 0.24)
    t = _radial_traj(8, 6)
    nPt = t.shape[1]
    y = _y(0, 2, nPt, zero=True)
    v = np.ones((1, nPt)) * 1e-4

    x = bmMathilda(y, t, v, None, N_u, N_u, dK_u)
    np.testing.assert_allclose(np.abs(x), 0, atol=1e-6)


def test_linearity():
    """bmMathilda(a*y + b*z) ≈ a*bmMathilda(y) + b*bmMathilda(z)."""
    N_u = [8, 8, 8]
    dK_u = list(np.ones(3) / 0.24)
    t = _radial_traj(8, 6)
    nPt = t.shape[1]
    rng = np.random.default_rng(5)
    y1 = _y(rng, 2, nPt)
    y2 = _y(rng, 2, nPt)
    v = np.ones((1, nPt)) * 1e-4
    a, b = np.complex64(2.0), np.complex64(-1.0)

    x1 = bmMathilda(y1, t, v, None, N_u, N_u, dK_u)
    x2 = bmMathilda(y2, t, v, None, N_u, N_u, dK_u)
    x_comb = bmMathilda((a * y1 + b * y2).astype(np.complex64), t, v, None, N_u, N_u, dK_u)

    np.testing.assert_allclose(x_comb, a * x1 + b * x2, rtol=1e-4, atol=1e-4)
