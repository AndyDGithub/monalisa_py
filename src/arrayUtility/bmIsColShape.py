import numpy as np


def bmIsColShape(x, N_u):
    x = np.asarray(x)
    N_u = np.array(N_u).ravel()
    nCh = x.size // int(np.prod(N_u))
    myColSize = (int(np.prod(N_u)), nCh)
    return x.shape == myColSize
