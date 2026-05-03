import numpy as np

def bmOutBorderMask3(M):
    """Bastien Milani
CHUV and UNIL
Lausanne - Switzerland
May 2023

This function return the inner mask for a matrix."""
    M = np.asarray(M)
    if M.ndim != 3:
        raise ValueError("Input must be a 3-D array")
    shape = tuple(np.array(M.shape) + 2)
    G = np.ones(shape, dtype=bool)
    G[1:-1, 1:-1, 1:-1] = False
    return G
