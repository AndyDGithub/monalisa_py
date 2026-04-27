import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape

def bmTraj_partialCartesian_ind_u(t, N_u, dK_u):
    N_u     = N_u.ravel().T
    dK_u    = dK_u.ravel().T
    imDim   = np.shape(N_u.ravel(), 1)

    t = bmPointReshape(t)

    if imDim == 1:
        ind_u =  1 + (t[0, :] - 1)
    elif imDim == 2:
        ind_u =  1 + (t[0, :] - 1) + N_u[0, 0] * (t[1, :] - 1)
    elif imDim == 3:
        ind_u =  1 + (t[0, :] - 1) + N_u[0, 0] * (t[1, :] - 1) + N_u[0, 0] * N_u[0, 1] * (t[2, :] - 1)

    return ind_u.astype(int)
