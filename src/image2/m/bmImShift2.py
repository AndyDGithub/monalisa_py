import numpy as np
from scipy.interpolate import interpn

def bmImShift2(im, s):
    s = s.ravel().T
    sx = s[0]
    sy = s[1]
    n_u = np.shape(im)
    nx = n_u[0]
    ny = n_u[1]

    X, Y = np.meshgrid(np.arange(1, nx + 1), np.arange(1, ny + 1))
    X2 = X - sx
    Y2 = Y - sy

    out = interpn((X, Y), im, (X2, Y2), method='cubic')
    out[np.isnan(out)] = 0

    return out
