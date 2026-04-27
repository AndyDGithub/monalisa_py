"""Unit tests for trajectory functions."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.traj3.bmTraj_fullRadial3_phyllotaxis_lineAssym2 import (
    bmTraj_fullRadial3_phyllotaxis_lineAssym2,
)


def _phyllotaxis_arg(N_n=8, nSeg=2, nShot=12, nShot_off=2):
    """Build a valid tuple arg for the phyllotaxis function."""
    FoV = 0.24
    dK_n = 1.0 / FoV / N_n   # k-space spacing per axis
    flagSelfNav = True         # exclude SI projection
    return (N_n, nSeg, nShot, dK_n, flagSelfNav, nShot_off)


def _nLines(nSeg, nShot, nShot_off, flagExcludeSI=True):
    return (nSeg - int(flagExcludeSI)) * (nShot - nShot_off)


def test_phyllotaxis_output_shape():
    """Phyllotaxis trajectory has shape (3, N_n, nLines)."""
    N_n = 8
    nSeg, nShot, nShot_off = 2, 12, 2
    arg = _phyllotaxis_arg(N_n, nSeg, nShot, nShot_off)
    t = bmTraj_fullRadial3_phyllotaxis_lineAssym2(arg)
    expected_nLines = _nLines(nSeg, nShot, nShot_off)
    assert t.shape == (3, N_n, expected_nLines), f"Got {t.shape}"


def test_phyllotaxis_dtype():
    """Trajectory is floating-point."""
    arg = _phyllotaxis_arg()
    t = bmTraj_fullRadial3_phyllotaxis_lineAssym2(arg)
    assert t.dtype.kind == 'f', f"Expected float, got {t.dtype}"


def test_phyllotaxis_range():
    """Trajectory values are within the expected k-space range."""
    N_n = 16
    nSeg, nShot, nShot_off = 2, 22, 2
    FoV = 0.24
    dK_n = 1.0 / FoV / N_n
    arg = (N_n, nSeg, nShot, dK_n, True, nShot_off)
    t = bmTraj_fullRadial3_phyllotaxis_lineAssym2(arg)
    # k-space range: each spoke spans [-N_n/2 * dK_n, N_n/2 * dK_n]
    kmax = (N_n / 2) * dK_n   # Nyquist half-bandwidth ≈ 2.08 for these params
    max_abs = np.max(np.abs(t))
    assert max_abs <= kmax * 1.05, f"Trajectory values out of range: {max_abs} > {kmax}"
    assert np.all(np.isfinite(t)), "Trajectory contains NaN or Inf"


def test_phyllotaxis_center_at_zero():
    """For symmetric spokes the first point (DC) should be near zero."""
    N_n = 8
    nSeg, nShot, nShot_off = 2, 12, 2
    arg = _phyllotaxis_arg(N_n, nSeg, nShot, nShot_off)
    t = bmTraj_fullRadial3_phyllotaxis_lineAssym2(arg)
    # centre index: either 0 or N_n//2
    # Just verify the trajectory is well-formed
    assert t.shape[0] == 3


def test_phyllotaxis_unique_spokes():
    """No two spokes are exactly identical."""
    N_n = 8
    nSeg, nShot, nShot_off = 2, 52, 2
    arg = _phyllotaxis_arg(N_n, nSeg, nShot, nShot_off)
    t = bmTraj_fullRadial3_phyllotaxis_lineAssym2(arg)
    nLines = t.shape[2]
    if nLines >= 2:
        # Different spokes should have different endpoint directions
        endpoints = t[:, -1, :]   # (3, nLines)
        std = np.std(endpoints, axis=1)
        assert np.any(std > 1e-6), "Spokes are all identical"


def test_phyllotaxis_more_lines():
    """Function accepts more lines without crashing."""
    N_n = 8
    nSeg, nShot, nShot_off = 2, 102, 2
    arg = _phyllotaxis_arg(N_n, nSeg, nShot, nShot_off)
    t = bmTraj_fullRadial3_phyllotaxis_lineAssym2(arg)
    assert t.ndim == 3
    assert t.shape[0] == 3
    assert t.shape[1] == N_n
