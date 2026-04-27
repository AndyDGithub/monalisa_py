import numpy as np
from src.arrayUtility import bmBlockReshape  # Import the required function


def bmCircular_ind_prev(nRank, ind_curr, index_mode):
    if index_mode == 'natural':
        ind_curr = ind_curr - 1  # Convert ind_curr to reduced index

    ind_prev = np.mod(ind_curr - 1 + nRank, nRank)  # Here is ind_prev a reduced index

    if index_mode == 'natural':
        ind_prev = ind_prev + 1  # Convert ind_prev to natural index

    return ind_prev
