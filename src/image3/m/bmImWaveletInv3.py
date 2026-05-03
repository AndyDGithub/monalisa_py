from __future__ import annotations

import numpy as np
from third_part.matlab_compat.matlab_native import isempty
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.varargin.bmVarargin import bmVarargin
from src.geom123 import bmTraj


def bmImWaveletInv3(cA, cH, cV, cD, n_u, *varargin):
    """Inverse single-level 2-D discrete wavelet transform.

    Parameters
    ----------
    cA, cH, cV, cD : array_like
        Approximation and detail coefficients of the 2-D wavelet transform.
transform.
    n_u : int or tuple
        Size used for reshaping the output with :func:`bmBlockReshape`.
    *varargin : object
        Optional arguments. The first element, if provided, is treated as t
the wavelet name. If omitted, the default wavelet ``'sym4'`` is used.

    Returns
    -------
    ndarray
        Reconstructed image after inverse transform and reshaping.

    Notes
    -----
    The implementation follows the original MATLAB logic:
    - Retrieve the wavelet name from ``varargin``.
    - If empty, default to ``'sym4'``.
    - Perform inverse DWT with periodic extension (`mode='per'`).
    - Reshape the result with :func:`bmBlockReshape`.
    """
    # Extract the first optional argument as the wavelet type, if any.
    wavelet_type_list = bmVarargin(*varargin)
    wavelet_type = wavelet_type_list[0] if wavelet_type_list else None

    # Default to 'sym4' when no wavelet type is specified.
    if isempty(wavelet_type):
        wavelet_type = "sym4"

    # Perform the inverse discrete wavelet transform.
    # pywt.idwt2 expects a tuple of (cA, (cH, cV, cD)).
    coeffs = (cA, (cH, cV, cD))
    x = pywt.idwt2(coeffs, wavelet=wavelet_type, mode="per")

    # Reshape the output to match the expected dimensions.
    x = bmBlockReshape(x, n_u)

    return x
