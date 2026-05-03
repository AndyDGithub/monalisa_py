from __future__ import annotations
import numpy as np
from third_part.matlab_compat.matlab_native import isempty
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.varargin.bmVarargin import bmVarargin

def bmImWaveletInv1(cA, cD, n_u, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # We use the function 'idwt' which performs an inverse single-level 1D
    # discrete wavelet transform.
    #
    # We use the wavelet_type 'sym4' by default.
    #
    # We use periodic extension.

    wavelet_type = bmVarargin(varargin)

    if isempty(wavelet_type):
        wavelet_type = 'sym4'  # magic

    cA = np.asarray(cA).flatten()
    cD = np.asarray(cD).flatten()

    x = idwt(cA, cD, wavelet_type, mode='per')
    x = bmBlockReshape(x, n_u)
    return x
