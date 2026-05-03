"""
bmSteva — iterative SENSE reconstruction with TV regularization (ADMM).

Port status: function signature and structure ported; numerical implementation
pending because it depends on bmNakatsha (adjoint NUFFT) which requires MEX.
"""
from __future__ import annotations
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmZero import bmZero
from src.fourier123.map_function.nonCartesian.bmShanna import bmShanna
from src.fourier123.prep_function.bmKF import bmKF
from src.fourier123.prep_function.bmKF_conj import bmKF_conj
from src.linSpace.bmProx_oneNorm import bmProx_oneNorm
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from src.optim.bmBackGradient import bmBackGradient
from src.optim.bmBackGradientT import bmBackGradientT


def bmSteva(x, z, u,
            y, ve, C,
            Gu, Gut, frSize,
            delta, rho, nCGD, ve_max,
            nIter, witnessInfo):
    """
    Iterative SENSE + TV reconstruction via ADMM (Split Bregman / Steva).

    Parameters
    ----------
    x          : initial image estimate, col format
    z, u       : ADMM auxiliary variables (None to initialize)
    y          : k-space data, (nPt, nCh) single
    ve         : volume elements
    C          : coil sensitivity maps, block format
    Gu         : forward gridding sparse matrix
    Gut        : backward gridding sparse matrix
    frSize     : frame (reconstruction) size
    delta      : regularization weight (scalar or 2-element)
    rho        : ADMM penalty (scalar or 2-element)
    nCGD       : number of conjugate gradient iterations per ADMM step
    ve_max     : maximum volume element clipping value
    nIter      : number of ADMM iterations
    witnessInfo: monitoring object

    Returns
    -------
    x : reconstructed image, block format
    """
    raise NotImplementedError(
        "bmSteva is not yet fully implemented. "
        "It requires bmNakatsha (adjoint NUFFT) which needs compiled MEX extensions."
    )


def _private_init_delta_rho(delta, rho, nIter):
    delta = np.abs(np.asarray(delta, dtype=np.float32).ravel())
    rho   = np.abs(np.asarray(rho,   dtype=np.float32).ravel())

    if delta.size == 1:
        delta = np.full(nIter, float(delta[0]), dtype=np.float32)
    elif delta.size == 2:
        delta = np.linspace(float(delta[0]), float(delta[1]), nIter, dtype=np.float32)

    if rho.size == 1:
        rho = np.full(nIter, float(rho[0]), dtype=np.float32)
    elif rho.size == 2:
        rho = np.linspace(float(rho[0]), float(rho[1]), nIter, dtype=np.float32)

    return delta, rho
