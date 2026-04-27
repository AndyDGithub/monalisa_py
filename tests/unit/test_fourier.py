"""Unit tests for bmDFT3 / bmIDF3."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.fourier3.bmDFT3 import bmDFT3
from src.fourier3.bmIDF3 import bmIDF3


def _ones_block(N=8, nCh=1):
    return np.ones((*([N] * 3), nCh), dtype=np.complex128)


def _random_block(N=8, nCh=2, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((*([N] * 3), nCh)) + 1j * rng.standard_normal((*([N] * 3), nCh))
    return x.astype(np.complex128)


def test_idf3_output_shape():
    """bmIDF3 returns same shape as input."""
    N = 8
    N_u = [N, N, N]
    dK_u = [1.0, 1.0, 1.0]
    x = _random_block(N, nCh=2)
    y = bmIDF3(x, N_u, dK_u)
    assert y.shape == x.shape


def test_dft3_output_shape():
    """bmDFT3 returns same shape as input."""
    N = 8
    N_u = [N, N, N]
    dK_u = [1.0, 1.0, 1.0]
    x = _random_block(N, nCh=2)
    y = bmDFT3(x, N_u, dK_u)
    assert y.shape == x.shape


def test_roundtrip_dft_idf():
    """DFT3(IDF3(x)) ≈ x (up to numerical precision)."""
    N = 8
    N_u = [N, N, N]
    dK_u = [0.125, 0.125, 0.125]   # arbitrary
    x = _random_block(N, nCh=1)
    roundtrip = bmDFT3(bmIDF3(x, N_u, dK_u), N_u, dK_u)
    np.testing.assert_allclose(roundtrip, x, rtol=1e-10, atol=1e-10)


def test_roundtrip_idf_dft():
    """IDF3(DFT3(x)) ≈ x."""
    N = 8
    N_u = [N, N, N]
    dK_u = [0.2, 0.2, 0.2]
    x = _random_block(N, nCh=2)
    roundtrip = bmIDF3(bmDFT3(x, N_u, dK_u), N_u, dK_u)
    np.testing.assert_allclose(roundtrip, x, rtol=1e-6, atol=1e-6)


def test_idf3_linearity():
    """IDF3 is linear."""
    N = 8
    N_u = [N, N, N]
    dK_u = [1.0, 1.0, 1.0]
    x1 = _random_block(N, seed=0)
    x2 = _random_block(N, seed=1)
    a, b = 2.0 + 1j, -1.0

    y1 = bmIDF3(x1, N_u, dK_u)
    y2 = bmIDF3(x2, N_u, dK_u)
    y_comb = bmIDF3(a * x1 + b * x2, N_u, dK_u)

    np.testing.assert_allclose(y_comb, a * y1 + b * y2, rtol=1e-10, atol=1e-10)


def test_idf3_scaling():
    """IDF3 applies scaling factor prod(N_u) * prod(dK_u)."""
    N = 4
    N_u = [N, N, N]
    dK_u = [0.5, 0.5, 0.5]
    # All-zero input except DC: x[N//2, N//2, N//2, 0] = 1
    x = np.zeros((N, N, N, 1), dtype=np.complex128)
    x[N // 2, N // 2, N // 2, 0] = 1.0   # DC component (centered)
    y = bmIDF3(x, N_u, dK_u)
    expected_scale = N ** 3 * 0.5 ** 3
    # After IDF of DC=1, spatial domain should be constant = scale * (1/N^3) everywhere
    np.testing.assert_allclose(np.abs(y), expected_scale / N ** 3, rtol=1e-6)


def test_dft3_multi_channel_independent():
    """Each channel is transformed independently."""
    N = 8
    N_u = [N, N, N]
    dK_u = [1.0, 1.0, 1.0]
    x = _random_block(N, nCh=3)
    y = bmDFT3(x, N_u, dK_u)
    for ch in range(3):
        x_ch = x[..., ch:ch+1]
        y_ch = bmDFT3(x_ch, N_u, dK_u)
        np.testing.assert_allclose(y[..., ch], y_ch[..., 0], rtol=1e-12)


def test_idf3_col_format_input():
    """bmIDF3 accepts flat col-format (Nu_tot, nCh) and returns same shape."""
    N = 8
    N_u = [N, N, N]
    dK_u = [1.0, 1.0, 1.0]
    Nu_tot = N ** 3
    x_flat = np.random.randn(Nu_tot, 2).astype(np.complex128)
    y = bmIDF3(x_flat, N_u, dK_u)
    assert y.shape == x_flat.shape
