"""Iterative non-Cartesian SENSE solver (bmSensa).

Port of `bmSensa.m`:
- outer iterations (`nIter`)
- inner conjugate-gradient descent iterations (`nCGD`)
- forward operator: bmShanna
- adjoint operator: bmNakatsha
"""
from __future__ import annotations

import numpy as np

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.fourier123.map_function.nonCartesian.bmNakatsha import bmNakatsha
from src.fourier123.map_function.nonCartesian.bmShanna import bmShanna
from src.fourier123.prep_function.bmKF import bmKF
from src.fourier123.prep_function.bmKF_conj import bmKF_conj
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from third_part.matlab_compat.matlab_native import double, single


def _to_col_vec(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x)
    if arr.ndim == 1:
        return arr.reshape(-1, 1)
    return arr


def _weighted_inner(x: np.ndarray, w: np.ndarray) -> float:
    xv = np.asarray(x).reshape(-1)
    wv = np.asarray(w).reshape(-1)
    return float(np.real(np.vdot(xv, wv)))


def _set_residu_slot(witnessInfo, c: int, value: float) -> None:
    if witnessInfo is None or not hasattr(witnessInfo, "param"):
        return
    try:
        # MATLAB indexing would store residual at slot 8 (1-based),
        # hence index 7 in Python.
        resid = witnessInfo.param[7]
        if isinstance(resid, np.ndarray):
            if resid.ndim == 2:
                resid[0, c] = value
            else:
                resid[c] = value
    except Exception:
        # Keep solver robust if witness object is partially configured.
        return


def _safe_watch(witnessInfo, *args) -> None:
    if witnessInfo is None:
        return
    watch = getattr(witnessInfo, "watch", None)
    if callable(watch):
        watch(*args)


def private_init_witnessInfo(witnessInfo, argName, frSize, N_u, dK_u, nIter, nCGD, ve_max):
    if witnessInfo is None:
        return
    if getattr(witnessInfo, "param_name", None) is None:
        witnessInfo.param_name = [None] * 8
    if getattr(witnessInfo, "param", None) is None:
        witnessInfo.param = [None] * 8

    witnessInfo.param_name[0] = "recon_name"
    witnessInfo.param[0] = argName

    witnessInfo.param_name[1] = "dK_u"
    witnessInfo.param[1] = dK_u

    witnessInfo.param_name[2] = "N_u"
    witnessInfo.param[2] = N_u

    witnessInfo.param_name[3] = "frSize"
    witnessInfo.param[3] = frSize

    witnessInfo.param_name[4] = "nIter"
    witnessInfo.param[4] = nIter

    witnessInfo.param_name[5] = "nCGD"
    witnessInfo.param[5] = nCGD

    witnessInfo.param_name[6] = "ve_max"
    witnessInfo.param[6] = ve_max

    witnessInfo.param_name[7] = "residu"
    witnessInfo.param[7] = np.zeros((1, int(nIter)), dtype=np.float64)


def bmSensa(x, y, ve, C, Gu, Gut, frSize, nCGD, ve_max, nIter, witnessInfo):
    myEps = 10 * np.finfo(np.float32).eps

    y = _to_col_vec(single(y))
    nCh = int(y.shape[1])
    N_u = double(single(np.asarray(Gu.N_u).ravel()))
    frSize = double(single(np.asarray(frSize).ravel()))
    dK_u = double(single(np.asarray(Gu.d_u).ravel()))

    C = single(bmColReshape(C, N_u))
    ve = single(bmY_ve_reshape(ve, y.shape))

    KFC = single(
        bmColReshape(
            bmKF(C, N_u, frSize, dK_u, nCh, Gu.kernel_type, Gu.nWin, Gu.kernelParam),
            frSize,
        )
    )
    KFC_conj = single(
        bmColReshape(
            bmKF_conj(np.conj(C), N_u, frSize, dK_u, nCh, Gu.kernel_type, Gu.nWin, Gu.kernelParam),
            frSize,
        )
    )

    x = single(bmColReshape(x, frSize))

    dX_u = single((1.0 / single(dK_u)) / single(N_u))
    HX = float(np.prod(dX_u.ravel()))

    if ve_max is None or np.size(ve_max) == 0:
        ve_max = np.max(ve)
    HY = np.minimum(ve, single(ve_max)).astype(np.float32, copy=False)

    private_init_witnessInfo(witnessInfo, "sensa", frSize, N_u, dK_u, int(nIter), int(nCGD), ve_max)

    c = 0
    for c in range(int(nIter)):
        res_next = y - bmShanna(x, Gu, KFC, frSize, "MATLAB")
        dagM_res_next = (1.0 / HX) * bmNakatsha(HY * res_next, Gut, KFC_conj, True, frSize, "MATLAB")

        sqn_dagM_res_next = _weighted_inner(dagM_res_next, HX * dagM_res_next)
        p_next = dagM_res_next

        for i in range(int(nCGD)):
            res_curr = res_next
            sqn_dagM_res_curr = sqn_dagM_res_next
            p_curr = p_next

            if sqn_dagM_res_curr < myEps:
                break

            Mp_curr = bmShanna(p_curr, Gu, KFC, frSize, "MATLAB")
            sqn_Mp_curr = _weighted_inner(Mp_curr, HY * Mp_curr)
            if sqn_Mp_curr <= myEps:
                break

            a = sqn_dagM_res_curr / sqn_Mp_curr
            x = x + a * p_curr

            if i == int(nCGD) - 1:
                break

            res_next = res_curr - a * Mp_curr
            dagM_res_next = (1.0 / HX) * bmNakatsha(HY * res_next, Gut, KFC_conj, True, frSize, "MATLAB")
            sqn_dagM_res_next = _weighted_inner(dagM_res_next, HX * dagM_res_next)
            if sqn_dagM_res_curr <= myEps:
                break
            b = sqn_dagM_res_next / sqn_dagM_res_curr
            p_next = dagM_res_next + b * p_curr

        temp_r = y - bmShanna(x, Gu, KFC, frSize, "MATLAB")
        R = _weighted_inner(temp_r, HY * temp_r)
        _set_residu_slot(witnessInfo, c, R)
        _safe_watch(witnessInfo, c, x, frSize, "loop")

    _safe_watch(witnessInfo, c, x, frSize, "final")
    return bmBlockReshape(x, frSize)
