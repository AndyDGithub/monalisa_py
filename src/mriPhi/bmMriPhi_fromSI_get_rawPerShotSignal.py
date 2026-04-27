import numpy as np
from src.arrayUtility import bmBlockReshape, bmCol

def unknown_function():
    ind_SI_min, ind_SI_max = None, None
    N = rmsSI.shape[1]
    L = rmsSI.shape[2]

    temp_x = np.tile(bmCol(range(N)), [L, 1]).T
    s = rmsSI[ind_SI_min:ind_SI_max, :]
    temp_x = temp_x[ind_SI_min:ind_SI_max, :]

    s = np.mean(s, axis=1)
    # s = np.sum(temp_x * s, axis=1) / np.sum(s, axis=1)

    s = s - np.mean(s.ravel())
    s = s / np.std(s.ravel())

    if ind_SI_max is not None:
        s = -s

    return s

def bmMriPhi_fromSI_get_rawPerShotSignal(rmsSI, ind_SI_min, ind_SI_max, s_reverse_flag=False):
    return unknown_function(rmsSI, ind_SI_min, ind_SI_max, s_reverse_flag)
