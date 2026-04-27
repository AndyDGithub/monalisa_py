import numpy as np
from third_part.matlab_compat.matlab_native import double, single

def bmInterp1(x, y, k):
    x = x.ravel().T
    k = k.ravel().T
    nSignal = np.shape(y, 1)
    nPt = np.shape(k, 2)
    out = np.zeros((nSignal, nPt), dtype=np.float64)

    for i in range(nSignal):
        out[i, :] = np.interp(k[:, 0], x, y[i, :], kind='pchip')

    if y.dtype == np.dtype('single'):
        out = single(out)
    elif y.dtype == np.dtype('double'):
        out = double(out)

    return out
