"""
bmTevaMorphosia_partialCartesian - multi-frame iterative partial-Cartesian reconstruction.

Port status: structure ported; numerical implementation pending.
"""
from __future__ import annotations
import numpy as np


def bmTevaMorphosia_partialCartesian(x, z, u,
                                     y, ve, C,
                                     N_u, dK_u, frSize,
                                     ind_u,
                                     Tu, Tut,
                                     delta, rho, regul_mode,
                                     nCGD, ve_max,
                                     nIter, witnessInfo):
    """
    Multi-frame iterative partial-Cartesian SENSE + motion reconstruction via ADMM.

    Parameters
    ----------
    x          : list of frame images
    z, u       : ADMM auxiliary variables
    y          : list of partial-Cartesian k-space data per frame
    ve         : volume elements per frame
    C          : coil sensitivity maps
    N_u        : Cartesian grid size
    dK_u       : grid step
    frSize     : frame size
    ind_u      : list of partial-Cartesian index sets per frame
    Tu, Tut    : deformation fields and transposes per frame
    delta      : regularization weight
    rho        : ADMM penalty
    regul_mode : 'normal' or 'adapt'
    nCGD       : CG iterations per ADMM step
    ve_max     : max volume element
    nIter      : ADMM iterations
    witnessInfo: monitoring object

    Returns
    -------
    x : reconstructed frames, block format
    """
    raise NotImplementedError(
        "bmTevaMorphosia_partialCartesian is not yet implemented."
    )


def _private_adapt_delta_rho(R, TV, delta_factor, rho_factor):
    delta = delta_factor * TV / (R + 1e-12)
    rho   = rho_factor * delta
    return delta, rho
