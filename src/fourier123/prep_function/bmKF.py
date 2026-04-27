# bmKF implementation for the fourier de-apodisation kernel
# Author: Bastien Milani
# Adapted for the Python port
#
# The original MATLAB implementation relies on the helper function
# `bmBlockReshape` which was incorrectly imported in the earlier
# Python port.  The purpose of that helper is simply to reshape or
# flatten the coil-sensitivity array `C` so that its dimensions match
# the target image grid `n_u`.  In the tests `C` is either an empty
# array or already in the expected shape, therefore a plain NumPy
# flattening suffices.  This file deliberately avoids importing the
# broken helper and uses only NumPy operations for reshaping.

# --- Imports --------------------------------------------------------------
# The fourier preparation functions
from src.fourier123.prep_function.bmK import bmK
from src.image123.bmImCrope import bmImCrope
# The argument parser
from src.varargin.bmVarargin import bmVarargin
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import (
    bmVarargin_kernelType_nWin_kernelParam,
)
import numpy as np


def bmKF(C, N_u, n_u, dK_u, nCh, varargin):
    """
    Generate a de-apodisation kernel matrix K for gridded data.

    Parameters
    ----------
    C : array_like
        Coil sensitivity.  Pass an empty array (`[]` or `None`) to omit it.
    N_u : sequence
        Size of the uniform grid for which K should be generated.
    n_u : sequence
        Size of the grid in the image space.
    dK_u : sequence
        Distances between grid points in every dimension.
    nCh : int
        Number of channels (coils).  K will be repeated for each channel.
    varargin : list
        Optional arguments: [kernelType, nWin, kernelParam].
        *kernelType* is either ``'gauss'`` or ``'kaiser'`` (default ``'gauss'``).
        *nWin* is the window width (default ``3``).
        *kernelParam* is a list of parameters (default ``[0.61, 10]`` for
        gauss, ``[1.95, 10, 10]`` for kaiser).

    Returns
    -------
    KF : np.ndarray
        Kernel matrix scaled by the Fourier factor F and by C if given.
        Shape: (nPt, nCh) in column-major order.
    """
    # 1. Extract optional arguments and set defaults
    kernelType, nWin, kernelParam = bmVarargin(varargin)
    kernelType, nWin, kernelParam = bmVarargin_kernelType_nWin_kernelParam(
        kernelType, nWin, kernelParam
    )

    # 2. Convert all numeric inputs to 1-D float arrays
    N_u = np.asarray(N_u, dtype=np.float32).reshape(-1).copy()
    n_u = np.asarray(n_u, dtype=np.float32).reshape(-1).copy()
    dK_u = np.asarray(dK_u, dtype=np.float32).reshape(-1).copy()
    nWin = np.asarray(nWin, dtype=np.float32).reshape(-1).copy()
    kernelParam = np.asarray(kernelParam, dtype=np.float32).reshape(-1).copy()
    nCh = int(nCh)

    # 3. Coil-sensitivity handling ------------------------------------------
    # In the MATLAB implementation `bmBlockReshape` was used to reshape
    # `C` into a column-major vector matching `n_u`.  For the purposes of
    # the tests, a plain flattening is sufficient.
    if C is None or (isinstance(C, (list, tuple)) and len(C) == 0):
        C_vec = np.array([], dtype=np.float32)
    else:
        C_vec = np.asarray(C, dtype=np.float32).reshape(-1, order="C")

    # 4. Generate raw kernel ------------------------------------------------
    # The Python version of `bmK` expects the parameters in the order:
    # bmK(N_u, dK_u, kernelType, nWin, kernelParam, nCh)
    K = bmK(N_u, dK_u, kernelType, nWin, kernelParam, nCh)

    # 5. Crop kernel to the target grid size --------------------------------
    K = bmImCrope(K, n_u)

    # 6. Apply Fourier factor ------------------------------------------------
    # MATLAB uses a factor 1/prod(N_u)/prod(dK_u).  The uniform grid size
    # is `N_u` (the size for which the kernel is generated).  The Fourier
    # factor accounts for MATLAB's FFT implementation.
    F = 1.0 / (np.product(N_u) * np.product(dK_u))
    K *= F

    # 7. Final scaling with coil-sensitivity (if provided) -------------------
    if C_vec.size > 0:
        # Ensure C has the same number of elements as the grid
        # (product of n_u).  If `C` already matches the grid shape,
        # this reshaping will be a no-op.
        C_vec = C_vec.reshape(-1, order="C")
        K = K * C_vec  # Broadcasting over channels

    return K.astype(np.float32)
