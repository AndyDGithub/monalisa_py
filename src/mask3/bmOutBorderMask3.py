import numpy as np

def bmOutBorderMask3(M):
    G = np.ones((np.array(M) + 2).tolist(), dtype=bool)
    G[1:-1, 1:-1, 1:-1] = False
    return G
