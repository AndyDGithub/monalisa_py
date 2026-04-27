from third_part.matlab_compat.matlab_native import double
import numpy as np
from src.function1.bmBump import bmBump  # Import bmBump function from existing source

def bmDoor2Bump(m, jump_width):
    myEps = np.abs(100 * np.finfo(float).eps)
    m = double(m)
    m -= np.min(m.ravel())
    m /= np.max(m.ravel())
    m = m.ravel().T

    myInd = np.arange(m.shape[1])  # Replace TODO with numpy array range
    max_mask = (m >= 1 - myEps)
    myInd_max = myInd[max_mask]
    ind_1 = np.min(myInd_max)
    ind_2 = np.max(myInd_max)
    delta_ind = int(np.ceil(jump_width))
    ind_3 = ind_1 + delta_ind
    ind_4 = ind_2 - delta_ind

    if ind_4 < ind_3:
        temp = ind_3
        ind_3 = ind_4
        ind_4 = temp

    if (ind_3 <= ind_1) or (ind_4 >= ind_2):
        raise ValueError('The factor is too large. ')

    bump_ind = ind_3 - ind_1 + 1
    half_bump_width = int((len(bump_ind) - 1) / 2) + 1
    myBump = bmBump(bump_ind, abs(bump_ind[0]))
    myBump = myBump[:, :half_bump_width]

    y = m.copy()
    y[:, ind_1-1:ind_3+1] = myBump
    y[:, ind_4:] = np.flip(myBump, axis=1)

    return y
