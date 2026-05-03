from __future__ import annotations

import numpy as np
from src.image123.bmImShiftList_to_image import bmImShiftList_to_image
from src.imDisp.bmImage import bmImage  # use the image helper
from src.image123.bmImResize import bmBlockReshape, bmVarargin  # Import bm
bmBlockReshape and bmVarargin

def bmImWavelet1(x, n_u, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # We use the function 'dwt' which performs a single-level 1D discrete
    # wavelet transform.
    # 
    # We use the wavelet_type 'sym4' by default.
    # 
    # We use periodic extension.
    
    # MATLAB body snapshot (untranslated, kept for parity context)
    wavelet_type = bmVarargin(varargin) if bmVarargin else 'sym4'
    n_u = n_u.flatten()
    x = bmBlockReshape(x, n_u)
    
    import pywt
    cA, cD = pywt.wavedec(x, wavelet_type, mode='per')
    
    return cA, cD
