"""Auto-generated from MATLAB source. Review manually before production use."""

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# This function returns the inner mask for a matrix.


import numpy as np


def bm2DimInBorderMask(M):
    G = np.ones_like(M, dtype=bool)
    G[1:-1, 1:-1] = False

    return G
