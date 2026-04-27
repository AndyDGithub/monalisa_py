import numpy as np

def bmOutBorderMask2(M):
    G = np.ones((M.shape[0] + 2, M.shape[1] + 2), dtype=bool)
    G[1:-1, 1:-1] = False
    return G
