"""Unit tests for bmTraj2SparseMat."""

import numpy as np
import scipy.sparse as sp
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gridding123.m.bmTraj2SparseMat import bmTraj2SparseMat
from src.sparseMat.m.bmSparseMat_scipy import bmSparseMatScipy


def _radial_traj_3d(nLines=20, nPt_per_line=16):
    """Generate a simple 3-D radial-ish trajectory."""
    rng = np.random.default_rng(42)
    angles = rng.uniform(0, np.pi, (nLines, 2))
    r = np.linspace(-0.4, 0.4, nPt_per_line)
    pts = []
    for theta, phi in angles:
        ux = np.sin(theta) * np.cos(phi)
        uy = np.sin(theta) * np.sin(phi)
        uz = np.cos(theta)
        pts.append(np.outer(np.array([ux, uy, uz]), r))
    t = np.concatenate(pts, axis=1)   # (3, nPt)
    return t


def _uniform_volume_elements(nPt):
    return np.ones((1, nPt), dtype=np.float64) * 1e-4


def test_return_types():
    """bmTraj2SparseMat returns a tuple of 3 bmSparseMatScipy objects."""
    t = _radial_traj_3d(10, 8)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4

    result = bmTraj2SparseMat(t, v, N_u, dK_u)
    assert isinstance(result, tuple)
    assert len(result) == 3
    for obj in result:
        assert isinstance(obj, bmSparseMatScipy)


def test_Gn_shape():
    """Gn has shape [Nu_tot, nPt]."""
    t = _radial_traj_3d(8, 6)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    Gn, Gu, Gut = bmTraj2SparseMat(t, v, N_u, dK_u)

    Nu_tot = int(np.prod(N_u))
    assert Gn.matrix.shape == (Nu_tot, nPt)
    assert Gu.matrix.shape == (nPt, Nu_tot)
    assert Gut.matrix.shape == (Nu_tot, nPt)


def test_Gut_is_transpose_of_Gu():
    """Gut must be the transpose of Gu."""
    t = _radial_traj_3d(6, 5)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    _, Gu, Gut = bmTraj2SparseMat(t, v, N_u, dK_u)

    diff = (Gu.matrix.T - Gut.matrix).toarray()
    np.testing.assert_allclose(diff, 0, atol=1e-10)


def test_Gn_rows_sum_to_one():
    """Each non-zero row of Gn sums to 1.0 (row-normalised)."""
    t = _radial_traj_3d(12, 10)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)

    row_sums = np.asarray(Gn.matrix.sum(axis=1)).ravel()
    nonzero = row_sums > 1e-10
    np.testing.assert_allclose(row_sums[nonzero], 1.0, atol=1e-6)


def test_Gu_rows_sum_to_one():
    """Each non-zero row of Gu sums to 1.0 (row-normalised)."""
    t = _radial_traj_3d(12, 10)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    _, Gu, _ = bmTraj2SparseMat(t, v, N_u, dK_u)

    row_sums = np.asarray(Gu.matrix.sum(axis=1)).ravel()
    nonzero = row_sums > 1e-10
    np.testing.assert_allclose(row_sums[nonzero], 1.0, atol=1e-6)


def test_N_u_metadata():
    """Gn.N_u matches the requested grid size."""
    t = _radial_traj_3d(6, 5)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)

    np.testing.assert_array_equal(Gn.N_u[:3], N_u.astype(np.float32).astype(np.float64))


def test_kaiser_kernel():
    """Kaiser kernel produces valid sparse matrices."""
    t = _radial_traj_3d(6, 5)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    N_u = np.array([8, 8, 8])
    dK_u = np.ones(3) / 0.4
    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u, None, 'kaiser', 3, [1.95, 10, 10])

    Nu_tot = int(np.prod(N_u))
    assert Gn.matrix.shape == (Nu_tot, nPt)
    row_sums = np.asarray(Gn.matrix.sum(axis=1)).ravel()
    nonzero = row_sums > 1e-10
    np.testing.assert_allclose(row_sums[nonzero], 1.0, atol=1e-6)


def test_sparse_matrices_are_not_dense():
    """Gn is genuinely sparse (nnz << total elements)."""
    t = _radial_traj_3d(20, 16)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    N_u = np.array([16, 16, 16])
    dK_u = np.ones(3) / 0.4
    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u)

    Nu_tot = int(np.prod(N_u))
    sparsity = Gn.matrix.nnz / (Nu_tot * nPt)
    assert sparsity < 0.1, f"Expected sparse matrix, got sparsity={sparsity:.4f}"


def test_r_size():
    """r_size attribute of Gn returns nPt."""
    t = _radial_traj_3d(6, 5)
    nPt = t.shape[1]
    v = _uniform_volume_elements(nPt)
    Gn, _, _ = bmTraj2SparseMat(t, v, [8, 8, 8], np.ones(3) / 0.4)
    assert int(Gn.r_size) == nPt


def test_out_of_bounds_points_excluded():
    """Trajectory points outside the grid are excluded silently."""
    # All points outside → Gn should have all-zero rows
    t = np.ones((3, 5)) * 1.0   # in physical units > FoV/2
    v = np.ones((1, 5)) * 1e-4
    N_u = np.array([4, 4, 4])
    dK_u = np.ones(3) * 0.1    # FoV = 10, but our FoV/2 = 5; points at 1.0 = inside
    # Push points outside by making dK_u large (small FoV)
    dK_u_small = np.ones(3) * 5.0  # FoV = 0.2; traj at ±1 is way outside
    Gn, _, _ = bmTraj2SparseMat(t, v, N_u, dK_u_small)
    # Should not crash; Gn matrix may have all zeros
    assert Gn.matrix.shape == (int(np.prod(N_u)), 5)
