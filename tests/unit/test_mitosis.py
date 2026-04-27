"""Unit tests for bmMitosis."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.arrayUtility.bmMitosis import bmMitosis


def _make_data(nCh=3, nPt=10):
    y = np.random.randn(nCh, nPt).astype(np.float64)
    t = np.random.randn(3, nPt).astype(np.float64)
    return y, t


def test_single_mask_one_phase():
    """One phase: mask selects all points → output == input."""
    y, t = _make_data(nCh=3, nPt=8)
    mask = np.ones((1, 8), dtype=np.float64)  # all true, 1 phase

    y_phases, t_phases = bmMitosis(y, t, mask, n_tables=2)

    # Each is a list of N_tot=1 arrays
    assert len(y_phases) == 1
    assert len(t_phases) == 1
    np.testing.assert_array_equal(y_phases[0], y)
    np.testing.assert_array_equal(t_phases[0], t)


def test_single_mask_two_phases():
    """Two phases: mask splits 8 points into first 5 and last 3."""
    nPt = 8
    y, t = _make_data(nCh=2, nPt=nPt)
    mask = np.zeros((2, nPt), dtype=np.float64)
    mask[0, :5] = 1      # phase 0: first 5 points
    mask[1, 5:] = 1      # phase 1: last 3 points

    y_phases, t_phases = bmMitosis(y, t, mask, n_tables=2)

    assert len(y_phases) == 2
    assert y_phases[0].shape == (2, 5)
    assert y_phases[1].shape == (2, 3)
    np.testing.assert_array_equal(y_phases[0], y[:, :5])
    np.testing.assert_array_equal(t_phases[0], t[:, :5])
    np.testing.assert_array_equal(y_phases[1], y[:, 5:])


def test_single_table():
    """n_tables=1 returns a tuple of 1 list."""
    y, _ = _make_data(nCh=2, nPt=6)
    mask = np.ones((1, 6))
    result = bmMitosis(y, mask, n_tables=1)
    assert len(result) == 1         # 1 table
    y_phases = result[0]
    assert len(y_phases) == 1       # 1 phase
    np.testing.assert_array_equal(y_phases[0], y)


def test_mask_as_list():
    """Masks passed as a Python list (cell-array style)."""
    y, t = _make_data(nCh=3, nPt=6)
    mask1 = np.ones((2, 6))
    mask1[1, :] = 0
    # Pass masks as a list (cell array convention)
    result = bmMitosis(y, [mask1], n_tables=1)
    y_phases = result[0]
    assert len(y_phases) == 2   # 2 phases from mask1


def test_n_tot_cartesian_product():
    """Two masks with 2 phases each → 4 total phases."""
    nPt = 12
    y = np.arange(nPt, dtype=float)[np.newaxis, :]  # (1, 12)
    mask1 = np.ones((2, nPt))
    mask2 = np.ones((2, nPt))
    # phase 0 of mask1: first 6 pts; phase 1: last 6 pts
    mask1[0, 6:] = 0
    mask1[1, :6] = 0
    # phase 0 of mask2: even indices; phase 1: odd indices
    mask2[0, 1::2] = 0
    mask2[1, 0::2] = 0

    result = bmMitosis(y, mask1, mask2, n_tables=1)
    y_phases = result[0]
    assert len(y_phases) == 4   # 2 x 2 = 4 phases


def test_mismatch_raises():
    """Mismatched last dimension raises ValueError."""
    y = np.ones((3, 10))
    t = np.ones((3, 8))   # different last dim
    mask = np.ones((1, 10))
    with pytest.raises(ValueError):
        bmMitosis(y, t, mask, n_tables=2)


def test_2d_mask_required():
    """1-D mask raises ValueError."""
    y = np.ones((3, 6))
    mask = np.ones(6)   # 1D
    with pytest.raises(ValueError):
        bmMitosis(y, mask, n_tables=1)


def test_no_mask_raises():
    """Omitting masks raises an error."""
    y = np.ones((3, 6))
    with pytest.raises((TypeError, ValueError)):
        bmMitosis(y, n_tables=1)


def test_output_concatenates_to_input():
    """All phase outputs concatenated along last axis equal the original (when mask covers all)."""
    nCh, nPt = 4, 12
    rng = np.random.default_rng(0)
    y = rng.standard_normal((nCh, nPt))
    # mask: 3 disjoint phases covering all points
    mask = np.zeros((3, nPt))
    mask[0, :4] = 1
    mask[1, 4:8] = 1
    mask[2, 8:] = 1

    result = bmMitosis(y, mask, n_tables=1)
    y_phases = result[0]
    y_concat = np.concatenate(y_phases, axis=-1)
    np.testing.assert_array_equal(y_concat, y)
