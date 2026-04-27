from src.linSpace.bmX_norm import bmX_norm
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.optim.bmBackGradient_n import bmBackGradient_n
import numpy as np


def bmTSV(x, N_u, dX_u):
    x = np.reshape(x, [np.prod(N_u).ravel(), 1])
    imDim = np.shape(N_u.ravel())[1]
    N_u = N_u.ravel().T
    dX_u = dX_u.ravel().T
    D_u = np.prod(dX_u.ravel())

    f = 0
    for n in range(imDim):
        g_part = bmBackGradient_n(x, N_u, dX_u, n)
        mySquaredNorm = D_u * bmX_norm(g_part, dX_u, True)**2
        f += mySquaredNorm

    return f
