import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bm2DimInBorderMask(M):
    """
    This function returns the inner mask for a matrix.
    
    Parameters:
    M (ndarray): The input matrix
    
    Returns:
    G (ndarray): The border mask
    """
    
    G = np.ones_like(M, dtype=bool)
    G[1:-1, 1:-1] = False

    return G
