import numpy as np


def bmIsBlockShape(x, N_u):
    x = np.asarray(x)
    N_u = np.array(N_u).ravel().astype(int)
    nCh = x.size // int(np.prod(N_u))
    myBlockSize = tuple(N_u) + (nCh,)
    return x.shape == myBlockSize
