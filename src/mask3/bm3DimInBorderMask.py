import numpy as np

def bm3DimInBorderMask(M):
    size = M.shape
    G = np.ones(size, dtype=bool)

    slice_start = 1 if len(size) == 3 else (1, 1)
    slice_stop = -1 if len(size) == 3 else (-1, -1)
    
    for dim in range(len(size)):
        G[slice_start[dim]:slice_stop[dim], ...] = False
        
    return G
