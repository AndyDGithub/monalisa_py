from src.arrayUtility.bmColReshape import bmColReshape
from third_part.matlab_compat.matlab_native import double

def bmGu_partialCartesian(x, ind_u, N_u):
    N_u = double(N_u.ravel().T)
    ind_u = double(ind_u.ravel())
    x = bmColReshape(x, N_u)

    y = x[ind_u, :]

    return y
