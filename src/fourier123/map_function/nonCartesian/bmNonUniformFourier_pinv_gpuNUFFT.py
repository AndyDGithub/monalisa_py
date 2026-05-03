from __future__ import annotations
import numpy as np


def bmNonUniformFourier_pinv_gpuNUFFT(y, t, ve, C, N_u, n_u, dK_u, ve_max):
    """
    Non-uniform Fourier pseudo-inverse reconstruction using gpuNUFFT.

    This function requires the gpuNUFFT MATLAB/CUDA library which is not
    available in the pure Python port. For Python-native NUFFT, use
    bmMathilda (Gaussian gridding) instead.

    Parameters
    ----------
    y     : (nPt, nCh)  complex  - k-space data
    t     : (3, nPt)    float    - k-space trajectory
    ve    : array-like           - volume elements (density compensation)
    C     : array or None        - coil sensitivity maps
    N_u   : array-like           - Cartesian grid size [Nx, Ny, Nz]
    n_u   : array-like or None   - output image size (= N_u if None)
    dK_u  : array-like           - grid step [dKx, dKy, dKz]
    ve_max: float                - maximum volume element value

    Returns
    -------
    x : ndarray - reconstructed image
    """
    raise NotImplementedError(
        "bmNonUniformFourier_pinv_gpuNUFFT requires the gpuNUFFT MATLAB/CUDA library. "
        "Use bmMathilda for Python-native gridded reconstruction."
    )
