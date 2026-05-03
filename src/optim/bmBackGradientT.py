from __future__ import annotations
import numpy as np

from src.optim.bmBackGradient_nT import bmBackGradient_nT

def bmBackGradientT(g, n_u, dX_u):
    """Strict deterministic baseline port from MATLAB."""
    imDim = len(n_u)
    nPt_u = np.prod(n_u)

    x = np.zeros((nPt_u, 1), dtype=np.complex64) 

    for n in range(imDim):
        x += bmBackGradient_nT(g[:, n], n_u, dX_u, n+1) 

    return x
