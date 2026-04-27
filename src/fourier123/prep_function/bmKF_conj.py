# bmKF_conj.py
# -------------------------------------------------------------------------
# This module implements the deapodization kernel matrix construction
# for data that was grid-to-uniform grid using window functions.
# -------------------------------------------------------------------------

import numpy as np

# Import the required helper functions
from src.fourier123.prep_function.bmK import bmK
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.image123.bmImCrope import bmImCrope
from src.varargin.bmVarargin import bmVarargin
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import (
    bmVarargin_kernelType_nWin_kernelParam,
)
from third_part.matlab_compat.matlab_native import single


def bmKF_conj(C_conj, N_u, n_u, dK_u, nCh, varargin):
    """
    Generates a deapodization kernel matrix scaled by the Fourier factor
    and optionally the conjugate coil sensitivity.

    Parameters
    ----------
    C_conj : array_like
        Conjugate of the coil sensitivity (conj(C)). Empty array to ignore.
    N_u : array_like
        Size of the uniform grid for which the kernel is generated.
    n_u : array_like
        Size of the grid in the image space.
    dK_u : array_like
        Distances between grid points in each dimension.
    nCh : int
        Number of channels (coils). The kernel is repeated for each channel.
    varargin : list
        Optional arguments in the order [kernelType, nWin, kernelParam].
        Default kernelType = 'gauss', nWin = 3, kernelParam = [0.61, 10].

    Returns
    -------
    KF_conj : np.ndarray
        Kernel matrix scaled by the Fourier factor and (optionally) the
        coil sensitivity.  The output is of type np.float32 in column
        format (nPt, nCh).
    """

    # Extract optional arguments and set defaults
    [kernelType, nWin, kernelParam] = bmVarargin(varargin)
    [kernelType, nWin, kernelParam] = bmVarargin_kernelType_nWin_kernelParam(
        kernelType, nWin, kernelParam
    )

    # Convert variables to the correct format
    C_conj      = single(bmBlockReshape(C_conj, n_u))
    N_u         = single(N_u.ravel().T)
    n_u         = single(n_u.ravel().T)
    dK_u        = single(dK_u.ravel().T)
    nWin        = single(nWin.ravel().T)
    kernelParam = single(kernelParam.ravel().T)
    nCh         = single(nCh)

    # Generate kernel matrix for deapodization
    K = single(bmK(N_u, dK_u, nCh, kernelType, nWin, kernelParam))

    # Crop data to grid of size n_u and return to column format
    K = bmImCrope(K, N_u, n_u)
    K = single(bmColReshape(K, n_u))

    # Fourier factor -> scaling needed due to MATLAB iFFT implementation
    F_conj = single(1 / np.prod(dK_u.ravel()))

    # Multiply K with F_conj, and with C_conj if C_conj is not empty
    if np.size(C_conj) == 0:
        KF_conj = single(K * F_conj)
    else:
        C_conj = single(bmColReshape(C_conj, n_u))
        KF_conj = single(K * F_conj * C_conj)

    return KF_conj
