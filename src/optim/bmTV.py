from src.optim.bmBackGradient import bmBackGradient
import numpy as np

def bmTV(x, N_u, dX_u):
    imDim = np.shape(N_u, 1)
    N_u = N_u.ravel().T
    dX_u = dX_u.ravel().T
    D_u = np.prod(dX_u)
    f = 0

    for n in range(imDim):
        g_part = bmBackGradient(x, N_u, dX_u, n)
        myNorm = np.sum(np.abs(g_part), axis=1) * D_u
        f += myNorm

    return f
