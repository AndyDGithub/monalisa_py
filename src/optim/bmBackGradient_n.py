from __future__ import annotations
from third_part.matlab_compat.matlab_native import size

from src.image123.bmImConv_inMask_byShiftList import circshift


def bmBackGradient_n(x, n_u, dX_u, n):
    """Strict deterministic baseline port from MATLAB."""
    # Get the dimensionality of n_u
    imDim = size(n_u, 1)
    
    # Ensure n_u and dX_u are column vectors
    n_u = n_u.flatten('F').reshape(-1, 1)
    dX_u = dX_u.flatten('F').reshape(-1, 1)
    
    # Initialize the shift vector
    myShift = np.zeros((1, imDim))
    myShift[0, n-1] = 1
    
    if imDim == 1:
        x = x.reshape(n_u, 1)
        g = (x - circshift(x, myShift)) / dX_u[0, n-1]
        if n == 1:
            g[0, 0] = 0
    elif imDim == 2:
        x = x.reshape((n_u[0], n_u[1]))
        g = (x - circshift(x, myShift)) / dX_u[0, n-1]
        if n == 1:
            g[0, :] = 0
        elif n == 2:
            g[:, 0] = 0
    elif imDim == 3:
        x = x.reshape((n_u[0], n_u[1], n_u[2]))
        g = (x - circshift(x, myShift)) / dX_u[0, n-1]
        if n == 1:
            g[0, :, :] = 0
        elif n == 2:
            g[:, 0, :] = 0
        elif n == 3:
            g[:, :, 0] = 0
    
    # Reshape the gradient to match the expected output
    g = g.reshape(-1)
    
    return g
