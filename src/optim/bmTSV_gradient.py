from src.optim.bmBackGradient_n import bmBackGradient_n
from src.optim.bmBackGradient_nT import bmBackGradient_nT

import numpy as np


def bmTSV_gradient(x, N_u, dX_u):
    """
    Compute the gradient of a function using the Total Variation (TV) metho
method.
    """
    # Ensure inputs are NumPy arrays and reshape as column vectors
    x = np.reshape(x, (np.prod(N_u), 1))
    N_u = np.asarray(N_u).reshape(-1)
    dX_u = np.asarray(dX_u).reshape(-1)
    imDim = len(N_u)
    D_u = np.prod(dX_u)

    g = np.zeros((np.prod(N_u), 1), dtype=np.complex64)

    # Loop over each dimension (1-based indexing as in MATLAB)
    for n in range(1, imDim + 1):
        g_part = bmBackGradient_n(x, N_u, dX_u, n)
        g += bmBackGradient_nT(g_part, N_u, dX_u, n)

    g *= 2 * D_u
    g = np.reshape(g, (np.prod(N_u), 1))

    return g
