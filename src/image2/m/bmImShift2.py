from __future__ import annotations
import numpy as np
from scipy.interpolate import interpn

def bmImShift2(im, s):
    """Strict deterministic baseline port from MATLAB."""
    # Translate MATLAB logic faithfully.
    s = np.atleast_2d(s).T
    sx = s[0, 0]
    sy = s[0, 1]

    n_u = im.shape
    nx, ny = n_u

    X, Y = np.meshgrid(np.arange(1, nx + 1), np.arange(1, ny + 1))
    X2 = X - sx
    Y2 = Y - sy

    out = interpn((X, Y), im, (X2, Y2), method='cubic')
    out[np.isnan(out)] = 0
    return out
