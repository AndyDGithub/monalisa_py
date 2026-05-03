# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

# This function return the inner mask for a matrix. 

import numpy as np


def bmOutBorderMask2(M):
    """Return the inner mask for a matrix.

    Parameters
    ----------
    M : ndarray
        Input matrix.

    Returns
    -------
    G : ndarray of bool
        Inner mask with True inside and False on the border.
    """
    
    G = np.ones((M.shape[0] + 2, M.shape[1] + 2), dtype=bool)
    G[1:-1, 1:-1] = False
    return G
