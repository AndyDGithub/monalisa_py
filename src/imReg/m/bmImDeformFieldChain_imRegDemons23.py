"""
bmImDeformFieldChain_imRegDemons23 — image registration deformation field chain.

Port status: requires MATLAB's imregdemons (Demons algorithm).
Use SimpleITK or dipy.align.imwarp as Python alternatives.
"""
from __future__ import annotations
import numpy as np


def bmImDeformFieldChain_imRegDemons23(x, n_u, chain_type, nIter, nSmooth, arg_name, varargin=None):
    """
    Compute a chain of deformation fields between frames using the Demons algorithm.

    Parameters
    ----------
    x          : array or list of images to register, block format
    n_u        : image size [Nx, Ny, Nz]
    chain_type : str - one of 'curr_to_prev', 'curr_to_next', 'prev_to_curr',
                 'next_to_curr', 'curr_to_first', 'first_to_curr'
    nIter      : number of Demons iterations (3-level pyramid: [nIter, nIter/2, nIter/4])
    nSmooth    : number of Gaussian smoothing iterations on images before registration
    arg_name   : str or None - save path for imDeformField output
    varargin   : optional (myMask, maxPixDisplacement)

    Returns
    -------
    imDeformField : list of deformation fields, one per frame
    im_out        : list of registered images

    Notes
    -----
    Python alternative: use SimpleITK.DemonsRegistrationFilter or
    dipy.align.imwarp.SymmetricDiffeomorphicRegistration.
    """
    raise NotImplementedError(
        "bmImDeformFieldChain_imRegDemons23 requires MATLAB's imregdemons. "
        "Python alternative: SimpleITK.DemonsRegistrationFilter."
    )
