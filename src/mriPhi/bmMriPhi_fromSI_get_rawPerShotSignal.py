import numpy as np
from src.arrayUtility.bmCol import bmCol


def bmMriPhi_fromSI_get_rawPerShotSignal(rmsSI, ind_SI_min, ind_SI_max, s_reverse_flag=False):
    N = rmsSI.shape[1]
    L = rmsSI.shape[2]

    temp_x = np.tile(bmCol(range(N)), [1, L])
    s = rmsSI[ind_SI_min:ind_SI_max, :]
    temp_x = temp_x[ind_SI_min:ind_SI_max, :]

    s = np.mean(s, axis=1)

    s = s - np.mean(s.ravel())
    s = s / np.std(s.ravel())

    if s_reverse_flag:
        s = -s

    return s
