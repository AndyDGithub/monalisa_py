from src.optim.bmBackGradient_n import bmBackGradient_n
from src.optim.bmBackGradient_nT import bmBackGradient_nT
import numpy as np

def bmTSV_gradient(x, N_u, dX_u):
    x = np.reshape(x, [np.prod(N_u), 1])
    imDim = np.shape(N_u, 1)
    N_u = N_u.T
    dX_u = dX_u.T
    D_u = np.prod(dX_u)
    g = np.zeros([np.prod(N_u), 1], "single")
    g = complex(g, g)
    
    for n in range(imDim):
        g_part = bmBackGradient_n(x, N_u, dX_u, n)
        g = g + bmBackGradient_nT(g_part, N_u, dX_u, n)
    g = 2 * D_u * g
    g = np.reshape(g, [np.prod(N_u), 1])

    return g
