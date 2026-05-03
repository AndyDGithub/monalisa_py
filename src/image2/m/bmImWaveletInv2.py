from __future__ import annotations

import numpy as np
from src.varargin.bmVarargin import bmVarargin
from src.image123.bmBlockReshape import bmBlockReshape

def bmImWaveletInv2(cA, cH, cV, cD, n_u, varargin):
    """Strict deterministic baseline port from MATLAB."""
    wavelet_type = bmVarargin(varargin)
    
    if not wavelet_type:
        wavelet_type = 'sym4'  # magic
    
    import scipy.signal as signal
    x = signal.idwt2(cA, cH, cV, cD, wavelet=wavelet_type, mode='per')
    
    x = bmBlockReshape(x, n_u)
    
    return x
