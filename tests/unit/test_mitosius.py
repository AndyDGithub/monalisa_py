"""Unit tests for bmMitosius_create and bmMitosius_load."""

import numpy as np
import os
import tempfile
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.mitosius.bmMitosius_create import bmMitosius_create
from src.mitosius.bmMitosius_load import bmMitosius_load


def _make_data(nCh=4, nSpoke=10, nPt_per_spoke=16):
    nPt = nSpoke * nPt_per_spoke
    rng = np.random.default_rng(0)
    y = (rng.standard_normal((nCh, nPt)) + 1j * rng.standard_normal((nCh, nPt))).astype(np.complex64)
    t = rng.standard_normal((3, nPt)).astype(np.float64) * 0.3
    v = np.abs(rng.standard_normal((1, nPt))).astype(np.float64) * 1e-4
    return y, t, v


def test_roundtrip():
    """bmMitosius_create then bmMitosius_load gives back identical arrays."""
    y, t, v = _make_data()
    with tempfile.TemporaryDirectory() as tmpdir:
        # API: pass lists (one element = one mitosius cell)
        bmMitosius_create(tmpdir, [y], [t], [v])
        y2 = bmMitosius_load(tmpdir, 'y')[0]
        t2 = bmMitosius_load(tmpdir, 't')[0]
        v2 = bmMitosius_load(tmpdir, 've')[0]

    np.testing.assert_allclose(y2, y, rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(t2, t, rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(v2, v, rtol=1e-5, atol=1e-5)


def test_roundtrip_shape():
    """Loaded arrays have the same shape as saved arrays."""
    y, t, v = _make_data(nCh=3, nSpoke=5, nPt_per_spoke=8)
    with tempfile.TemporaryDirectory() as tmpdir:
        bmMitosius_create(tmpdir, [y], [t], [v])
        y2 = bmMitosius_load(tmpdir, 'y')[0]
        t2 = bmMitosius_load(tmpdir, 't')[0]
        v2 = bmMitosius_load(tmpdir, 've')[0]

    assert y2.shape == y.shape
    assert t2.shape == t.shape
    assert v2.shape == v.shape


def test_files_created():
    """create produces files in the target directory."""
    y, t, v = _make_data()
    with tempfile.TemporaryDirectory() as tmpdir:
        bmMitosius_create(tmpdir, [y], [t], [v])
        files = os.listdir(tmpdir)
    assert len(files) > 0


def test_load_nonexistent_raises():
    """Loading from a nonexistent directory raises an error."""
    with pytest.raises(Exception):
        bmMitosius_load('/nonexistent/path/to/mitosius', 'y')


def test_multichannel_roundtrip():
    """Round-trip preserves multi-channel data correctly."""
    nCh = 8
    y, t, v = _make_data(nCh=nCh)
    with tempfile.TemporaryDirectory() as tmpdir:
        bmMitosius_create(tmpdir, [y], [t], [v])
        y2 = bmMitosius_load(tmpdir, 'y')[0]

    assert y2.shape[0] == nCh
    np.testing.assert_allclose(y2, y, rtol=1e-5, atol=1e-5)


def test_multi_cell_create_and_load():
    """Multi-cell mitosius: each cell loads independently."""
    y1, t1, v1 = _make_data(nCh=2, nSpoke=4, nPt_per_spoke=8)
    y2, t2, v2 = _make_data(nCh=2, nSpoke=5, nPt_per_spoke=8)
    with tempfile.TemporaryDirectory() as tmpdir:
        bmMitosius_create(tmpdir, [y1, y2], [t1, t2], [v1, v2])
        loaded_y = bmMitosius_load(tmpdir, 'y')
        loaded_t = bmMitosius_load(tmpdir, 't')

    assert len(loaded_y) == 2
    assert len(loaded_t) == 2
    np.testing.assert_allclose(loaded_y[0], y1, rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(loaded_y[1], y2, rtol=1e-5, atol=1e-5)


def test_create_empty_structure():
    """bmMitosius_create with integer length creates directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bmMitosius_create(tmpdir, 3)  # create 3-cell empty structure
        files = os.listdir(tmpdir)
    # Should have mitosius_size.mat + 3 cell dirs
    assert len(files) >= 4
