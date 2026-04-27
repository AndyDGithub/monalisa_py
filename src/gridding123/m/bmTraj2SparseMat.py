"""
bmTraj2SparseMat — non-Cartesian gridding sparse matrices.

Port of MATLAB bmTraj2SparseMat.m using scipy.sparse.
Always computes and returns Gn, Gu, Gut.
"""

import numpy as np
import scipy.sparse as sp

from src.arrayUtility.bmPointReshape import bmPointReshape
from src.sparseMat.m.bmSparseMat_scipy import bmSparseMatScipy
from src.varargin.bmVarargin import bmVarargin_unpack
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import (
    bmVarargin_kernelType_nWin_kernelParam,
)


def bmTraj2SparseMat(t, v, N_u, dK_u, *varargin):
    """
    Compute gridding sparse matrices Gn, Gu and Gut.

    Parameters
    ----------
    t : array (imDim, nPt)   — trajectory in physical k-space units
    v : array (1, nPt)       — density-compensation / volume elements
    N_u : array-like [Nx, Ny, Nz]
    dK_u : array-like [dKx, dKy, dKz]
    varargin : optional
        [sparseType, kernelType, nWin, kernelParam]
        Only 'gauss' and 'kaiser' kernelTypes are supported.
        sparseType is accepted but ignored (always returns bmSparseMatScipy).

    Returns
    -------
    (Gn, Gu, Gut) : tuple of bmSparseMatScipy
        Gn  [Nu_tot, nPt]  — normalized inverse gridding (traj → grid)
        Gu  [nPt, Nu_tot]  — forward gridding (grid → traj)
        Gut [Nu_tot, nPt]  — transpose of Gu (= Gu.T)
    """
    va = bmVarargin_unpack(list(varargin), 4)
    _sparseType, kernelType, nWin, kernelParam = va

    kernelType, nWin, kernelParam = bmVarargin_kernelType_nWin_kernelParam(
        kernelType, nWin, kernelParam
    )

    # ── type normalisation (matches MATLAB double(single(...)) pattern) ──────
    t = np.float64(bmPointReshape(t))                         # (imDim, nPt)
    Dn = np.float64(np.asarray(v).ravel())                   # (nPt,)
    N_u = np.float64(np.float32(np.asarray(N_u).ravel()))
    dK_u = np.float64(np.float32(np.asarray(dK_u).ravel()))
    nWin_f = float(np.float64(np.float32(nWin)))
    kp = np.float64(np.float32(np.atleast_1d(kernelParam)))

    imDim = int(t.shape[0])
    nPt = int(t.shape[1])

    # ── rescale trajectory to grid units ────────────────────────────────────
    Nx_u = int(N_u[0]) if imDim >= 1 else 0
    Ny_u = int(N_u[1]) if imDim >= 2 else 0
    Nz_u = int(N_u[2]) if imDim >= 3 else 0
    Nu_tot = 1
    Du = 1.0
    t = t.copy()

    myTrajShift = np.zeros(imDim)
    if imDim >= 1:
        t[0] /= dK_u[0]
        Dn /= dK_u[0]
        myTrajShift[0] = np.fix(Nx_u / 2 + 1)
        Du *= (1.0 / dK_u[0]) / Nx_u
        Nu_tot *= Nx_u
    if imDim >= 2:
        t[1] /= dK_u[1]
        Dn /= dK_u[1]
        myTrajShift[1] = np.fix(Ny_u / 2 + 1)
        Du *= (1.0 / dK_u[1]) / Ny_u
        Nu_tot *= Ny_u
    if imDim >= 3:
        t[2] /= dK_u[2]
        Dn /= dK_u[2]
        myTrajShift[2] = np.fix(Nz_u / 2 + 1)
        Du *= (1.0 / dK_u[2]) / Nz_u
        Nu_tot *= Nz_u

    t += myTrajShift[:, np.newaxis]   # shift to 1-indexed grid space

    # ── delete out-of-bounds trajectory points ──────────────────────────────
    deleteMask = np.zeros(nPt, dtype=bool)
    if imDim >= 1:
        deleteMask |= (t[0] < 1) | (t[0] > Nx_u)
    if imDim >= 2:
        deleteMask |= (t[1] < 1) | (t[1] > Ny_u)
    if imDim >= 3:
        deleteMask |= (t[2] < 1) | (t[2] > Nz_u)

    # ── build window grid (F-order neighbour offsets) ────────────────────────
    nWin_i = int(nWin_f)
    if nWin_i % 2 == 0:
        half = nWin_i // 2
        rng = np.arange(-half - 1, half + 1, dtype=np.float64)
        myFloorShift = np.zeros(imDim)
    else:
        half = int(np.fix(nWin_f / 2))
        rng = np.arange(-half, half + 1, dtype=np.float64)
        myFloorShift = np.full(imDim, 0.5)

    if imDim == 1:
        c = rng[np.newaxis, :]                       # (1, nNb)
    elif imDim == 2:
        cx, cy = np.meshgrid(rng, rng, indexing='ij')
        c = np.vstack([cx.ravel(), cy.ravel()])       # (2, nNb)
    else:
        cx, cy, cz = np.meshgrid(rng, rng, rng, indexing='ij')
        c = np.vstack([cx.ravel(), cy.ravel(), cz.ravel()])  # (3, nNb)

    nNb = c.shape[1]

    # ── per-point floor / remainder ──────────────────────────────────────────
    # t_floor : (imDim, nPt),  t_rest : (imDim, nPt)
    t_floor = np.floor(t + myFloorShift[:, np.newaxis])
    t_rest = t - t_floor

    # expand to (imDim, nNb, nPt)
    t_floor_3d = t_floor[:, np.newaxis, :] * np.ones((1, nNb, 1))
    t_rest_3d = t_rest[:, np.newaxis, :] * np.ones((1, nNb, 1))
    c_3d = c[:, :, np.newaxis] * np.ones((1, 1, nPt))

    # ── kernel weights ───────────────────────────────────────────────────────
    d = t_rest_3d - c_3d                             # (imDim, nNb, nPt)
    d_norm = np.sqrt(np.sum(d ** 2, axis=0))         # (nNb, nPt)

    if kernelType == 'gauss':
        sigma = float(kp.ravel()[0])
        myWeight = np.exp(-0.5 * (d_norm / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
    elif kernelType == 'kaiser':
        tau = float(kp.ravel()[0])
        alpha = float(kp.ravel()[1])
        I0alpha = float(np.i0(alpha))
        w = np.maximum(1.0 - (d_norm / tau) ** 2, 0.0)
        myWeight = np.i0(alpha * np.sqrt(w)) / I0alpha
    else:
        raise ValueError(f"Unknown kernelType: {kernelType!r}")

    # ── F-order linear grid indices (1-indexed MATLAB convention) ────────────
    n = t_floor_3d + c_3d                            # (imDim, nNb, nPt)
    if imDim == 1:
        n[0] = np.mod(n[0] - 1, Nx_u) + 1
        lin = (n[0] - 1).astype(np.int64)
    elif imDim == 2:
        n[0] = np.mod(n[0] - 1, Nx_u) + 1
        n[1] = np.mod(n[1] - 1, Ny_u) + 1
        lin = (n[0] - 1 + (n[1] - 1) * Nx_u).astype(np.int64)
    else:
        n[0] = np.mod(n[0] - 1, Nx_u) + 1
        n[1] = np.mod(n[1] - 1, Ny_u) + 1
        n[2] = np.mod(n[2] - 1, Nz_u) + 1
        lin = (n[0] - 1 + (n[1] - 1) * Nx_u + (n[2] - 1) * Nx_u * Ny_u).astype(np.int64)
    # lin: (nNb, nPt)

    # ── build index / weight arrays and apply deleteMask ────────────────────
    pt_idx = np.tile(np.arange(nPt, dtype=np.int64), (nNb, 1))  # (nNb, nPt)
    Dn_2d = np.tile(Dn, (nNb, 1))                                 # (nNb, nPt)
    valid_2d = np.tile(~deleteMask, (nNb, 1))                     # (nNb, nPt)

    gidx = lin.ravel()[valid_2d.ravel()]
    pidx = pt_idx.ravel()[valid_2d.ravel()]
    wgt  = myWeight.ravel()[valid_2d.ravel()]
    dn   = Dn_2d.ravel()[valid_2d.ravel()]

    # ── Gn [Nu_tot, nPt] ────────────────────────────────────────────────────
    Gn_raw = sp.csr_matrix((wgt * dn, (gidx, pidx)), shape=(Nu_tot, nPt))
    row_sums = np.asarray(Gn_raw.sum(axis=1)).ravel()
    row_sums[row_sums == 0] = 1.0
    Gn_mat = sp.diags(1.0 / row_sums, format='csr') @ Gn_raw

    # ── Gu [nPt, Nu_tot] ────────────────────────────────────────────────────
    Gu_raw = sp.csr_matrix((wgt * Du, (pidx, gidx)), shape=(nPt, Nu_tot))
    row_sums_u = np.asarray(Gu_raw.sum(axis=1)).ravel()
    row_sums_u[row_sums_u == 0] = 1.0
    Gu_mat = sp.diags(1.0 / row_sums_u, format='csr') @ Gu_raw

    Gut_mat = Gu_mat.T.tocsr()

    meta = dict(N_u=N_u, dK_u=dK_u, kernelType=kernelType, nWin=nWin_f, kernelParam=kp)

    def _wrap(mat, npt):
        sm = bmSparseMatScipy(mat, **{k: v for k, v in meta.items()})
        sm._nPt = npt
        return sm

    Gn_obj  = _wrap(Gn_mat,  nPt)
    Gu_obj  = _wrap(Gu_mat,  Nu_tot)   # Gu rows = nPt, cols = Nu_tot
    Gut_obj = _wrap(Gut_mat, nPt)

    return Gn_obj, Gu_obj, Gut_obj
