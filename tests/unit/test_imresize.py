"""Unit tests for bmImResize."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.image123.bmImResize import bmImResize


def _block_array(N_in, nCh=2, dtype=np.float64, seed=0):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((*([N_in] * 3), nCh)).astype(dtype)


def test_output_shape_upsample():
    """Upsampling doubles the spatial dimensions."""
    x = _block_array(8, nCh=2)
    out = bmImResize(x, [8, 8, 8], [16, 16, 16])
    assert out.shape == (16, 16, 16, 2)


def test_output_shape_downsample():
    """Downsampling halves the spatial dimensions."""
    x = _block_array(16, nCh=1)
    out = bmImResize(x, [16, 16, 16], [8, 8, 8])
    assert out.shape == (8, 8, 8, 1)


def test_identity_resize():
    """Resizing to the same size returns a result numerically close to input."""
    x = _block_array(8, nCh=1)
    out = bmImResize(x, [8, 8, 8], [8, 8, 8])
    assert out.shape == x.shape
    # Cubic interpolation at original sample points is exact to ~1e-4
    np.testing.assert_allclose(out, x, rtol=1e-3, atol=1e-3)


def test_complex_input():
    """Complex arrays are handled correctly."""
    rng = np.random.default_rng(1)
    x = (rng.standard_normal((8, 8, 8, 1)) + 1j * rng.standard_normal((8, 8, 8, 1))).astype(np.complex64)
    out = bmImResize(x, [8, 8, 8], [16, 16, 16])
    assert out.shape == (16, 16, 16, 1)
    assert np.iscomplexobj(out)


def test_constant_field_preserved():
    """A spatially constant field resizes to the same constant."""
    x = np.ones((8, 8, 8, 1), dtype=np.float64) * 3.7
    out = bmImResize(x, [8, 8, 8], [12, 12, 12])
    # Inner region (away from boundaries) should be ~3.7
    center = out[3:9, 3:9, 3:9, 0]
    np.testing.assert_allclose(center, 3.7, rtol=1e-4, atol=1e-4)


def test_multichannel_independence():
    """Each channel is interpolated independently."""
    rng = np.random.default_rng(2)
    x = rng.standard_normal((8, 8, 8, 3)).astype(np.float64)
    out = bmImResize(x, [8, 8, 8], [12, 12, 12])
    for ch in range(3):
        x_ch = x[..., ch:ch+1]
        out_ch = bmImResize(x_ch, [8, 8, 8], [12, 12, 12])
        np.testing.assert_allclose(out[..., ch], out_ch[..., 0], rtol=1e-10, atol=1e-10)


def test_output_finite():
    """Output has no NaN or Inf."""
    x = _block_array(8, nCh=2)
    out = bmImResize(x, [8, 8, 8], [12, 12, 12])
    assert np.all(np.isfinite(out))


def test_non_uniform_resize():
    """Non-uniform resize changes each axis independently."""
    x = _block_array(8, nCh=1)
    out = bmImResize(x, [8, 8, 8], [12, 8, 6])
    assert out.shape == (12, 8, 6, 1)
