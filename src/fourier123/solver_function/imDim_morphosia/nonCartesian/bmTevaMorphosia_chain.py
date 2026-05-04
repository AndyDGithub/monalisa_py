"""
bmTevaMorphosia_chain - multi-frame iterative reconstruction with motion (Teva Morphosia).

Port status: structure ported; numerical implementation pending (requires MEX).
"""
from __future__ import annotations
import numpy as np


def bmTevaMorphosia_chain(x, z, u,
                          y, ve, C,
                          Gu, Gut, frSize,
                          Tu, Tut,
                          delta, rho, regul_mode,
                          nCGD, ve_max,
                          nIter, witnessInfo):
    """
    Multi-frame iterative SENSE + motion reconstruction via ADMM.

    Parameters
    ----------
    x          : list of frame image estimates, col format
    z, u       : ADMM auxiliary variables (None to initialize)
    y          : list of k-space data per frame
    ve         : list of volume elements per frame
    C          : coil sensitivity maps, block format
    Gu         : list of forward gridding sparse matrices per frame
    Gut        : list of backward gridding sparse matrices per frame
    frSize     : frame (reconstruction) size
    Tu, Tut    : lists of deformation fields and their transposes
    delta      : regularization weight
    rho        : ADMM penalty parameter
    regul_mode : 'normal' or 'adapt'
    nCGD       : conjugate gradient iterations per ADMM step
    ve_max     : maximum volume element clipping value
    nIter      : ADMM iterations
    witnessInfo: monitoring object

    Returns
    -------
    x : list of reconstructed frames, block format
    """
    raise NotImplementedError(
        "bmTevaMorphosia_chain is not yet implemented. "
        "Requires MEX-based NUFFT and motion deformation operators."
    )


def _private_ve_to_HY(ve, ve_max, y):
    nFr = len(y) if isinstance(y, (list, tuple)) else 1
    HY  = [None] * nFr
    for i in range(nFr):
        ve_i = np.asarray(ve[i] if isinstance(ve, (list, tuple)) else ve, dtype=np.float32)
        HY[i] = np.minimum(ve_i, np.float32(ve_max))
    return HY


def _private_init_regul_param(in_param, nIter):
    p = np.abs(np.asarray(in_param, dtype=np.float32).ravel())
    if p.size == 1:
        return np.full(nIter, float(p[0]), dtype=np.float32)
    elif p.size == 2:
        return np.linspace(float(p[0]), float(p[1]), nIter, dtype=np.float32)
    return p
