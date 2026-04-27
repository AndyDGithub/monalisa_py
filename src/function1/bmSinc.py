import numpy as np
from src.arrayUtility import bmBlockReshape

def bmSinc(x):
    myEps = 1e-4
    f = np.sin(x) / x
    mask = np.isnan(f) | np.isinf(f) | ~np.isfinite(f) | (x == 0) | (np.abs(x) < myEps)
    f[mask] = 1
    return f
