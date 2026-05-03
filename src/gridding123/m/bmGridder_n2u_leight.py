from __future__ import annotations

import numpy as np

from src.arrayUtility.bmPointReshape import bmPointReshape
from src.gridding123.m.bmTraj2SparseMat import bmTraj2SparseMat
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import (
    bmVarargin_kernelType_nWin_kernelParam,
)


def bmGridder_n2u_leight(
    y,
    t,
    v,
    N_u,
    dK_u,
    kernelType=None,
    nWin=None,
    kernelParam=None,
    **kwargs,
):
    """
    Python fallback for non-Cartesian gridding.

    Builds `Gn` with `bmTraj2SparseMat` and applies it channel-wise.
    Output shape is `(nCh, *N_u)`.
    """
    kernelType, nWin, kernelParam = bmVarargin_kernelType_nWin_kernelParam(
        kernelType, nWin, kernelParam
    )

    t_2d = np.asarray(bmPointReshape(t), dtype=np.float64)
    y_2d = np.asarray(bmPointReshape(y), dtype=np.complex64)
    v_1d = np.asarray(bmPointReshape(v), dtype=np.float64).reshape(-1)

    if y_2d.ndim == 1:
        y_2d = y_2d.reshape(1, -1)
    if y_2d.shape[0] >= y_2d.shape[1]:
        y_2d = y_2d.T

    nCh, nPt = y_2d.shape
    if t_2d.ndim != 2 or t_2d.shape[1] != nPt:
        raise ValueError("Trajectory and data have incompatible point counts.")
    if v_1d.size != nPt:
        raise ValueError("Volume elements and data have incompatible point counts.")

    Gn, _, _ = bmTraj2SparseMat(
        t_2d,
        v_1d,
        N_u,
        dK_u,
        None,
        kernelType,
        nWin,
        kernelParam,
    )

    x_col = Gn.matrix @ y_2d.T  # (Nu_tot, nCh)
    x_col = np.asarray(x_col, dtype=np.complex64)

    N_u_int = tuple(int(v) for v in np.asarray(N_u).ravel())
    Nu_tot = int(np.prod(N_u_int))
    if x_col.shape[0] != Nu_tot:
        raise ValueError("Unexpected gridded vector size.")

    out = np.empty((nCh,) + N_u_int, dtype=np.complex64)
    for ch in range(nCh):
        out[ch] = x_col[:, ch].reshape(N_u_int, order="F")
    return out
