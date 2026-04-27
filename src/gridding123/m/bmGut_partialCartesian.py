from src.arrayUtility.bmColReshape import bmColReshape
from third_part.matlab_compat.matlab_native import double
import numpy as np

def bmGut_partialCartesian(y, ind_u, N_u):
    N_u = double(N_u.ravel().T)
    ind_u = double(ind_u.ravel())
    nCh = np.shape(y, 1)
    nPt = np.shape(y.ravel(), 0)//nCh
    y = bmColReshape(y, nPt)
    x = np.zeros((prod(N_u.ravel()), nCh), dtype="single")
    if not np.isrealobj(y):
        x = complex(x, x)
    for i in range(nCh):
        x[ind_u, i] = y[:, i]
    return x
