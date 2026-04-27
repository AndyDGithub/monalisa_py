import numpy as np
from src.image123.bmImResize import bmBlockReshape

def bmImGrid(n_u, X=None, Y=None, Z=None):
    n_u = n_u.ravel().T
    imDim = np.shape(n_u.ravel(), 1)

    if imDim == 2:
        if X is None or Y is None:
            [X, Y] = bmBlockReshape(np.arange(1, int(n_u[0])+1), np.arange(1, int(n_u[1])+1))
    elif imDim == 3:
        if X is None or Y is None or Z is None:
            [X, Y, Z] = bmBlockReshape(np.arange(1, int(n_u[0])+1), np.arange(1, int(n_u[1])+1), np.arange(1, int(n_u[2])+1))

    return (X, Y, Z)
