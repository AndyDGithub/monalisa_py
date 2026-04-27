from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.varargin.bmVarargin import bmVarargin
import numpy as np

def bmImWavelet2(x, n_u, varargin):
    wavelet_type = bmVarargin(varargin)
    # Assign default value if none provided
    if not wavelet_type:
        wavelet_type = 'sym4'  # magic

    n_u = np.ravel(n_u).T
    x = bmBlockReshape(x, n_u)
    
    [cA, cH, cV, cD] = np.dwt2(x, wavelet_type, mode='per')
    
    return (cA, cH, cV, cD)
