import numpy as np
from src.arrayUtility import bmBlockReshape

def bmCircular_ind_next(nRank, ind_curr, index_mode):
    # Convert ind_curr to reduced index
    ind_curr = ind_curr - 1

    ind_next = np.mod(ind_curr + 1, nRank)

    # Convert ind_next to natural index if needed
    if index_mode == 'natural':
        ind_next = ind_next + 1

    return int(ind_next)
