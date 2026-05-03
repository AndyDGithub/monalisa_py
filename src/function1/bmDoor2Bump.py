from third_part.matlab_compat.matlab_native import double
import numpy as np
from src.function1.bmBump import bmBump


def bmDoor2Bump(m, jump_width):
    """
    MATLAB: bmDoor2Bump.m
    Create a "door" bump in a 1-D array.

    Parameters
    ----------
    m : array_like
        Input signal.
    jump_width : int
        Width of the jump in samples.

    Returns
    -------
    y : np.ndarray
        Signal with the door bump applied.
    """
    myEps = np.abs(100 * np.finfo(float).eps)

    # Normalise the input signal
    m = double(m)
    m = m - np.min(m.ravel())
    m = m / np.max(m.ravel())
    m = m.ravel()  # 1-D array

    # Find indices where the signal is close to 1
    myInd = np.arange(m.size)
    max_mask = (m >= 1 - myEps)
    myInd_max = myInd[max_mask]
    if myInd_max.size == 0:
        raise ValueError("No samples close to 1 found.")

    ind_1 = np.min(myInd_max)
    ind_2 = np.max(myInd_max)

    delta_ind = int(np.ceil(jump_width))
    ind_3 = ind_1 + delta_ind
    ind_4 = ind_2 - delta_ind

    if ind_4 < ind_3:
        ind_3, ind_4 = ind_4, ind_3

    if (ind_3 <= ind_1) or (ind_4 >= ind_2):
        raise ValueError("The factor is too large.")

    # Construct the bump index array
    bump_len = ind_3 - ind_1 + 1
    bump_ind = np.arange(-bump_len, bump_len + 1)
    half_bump_width = len(bump_ind) // 2 + 1

    # Generate the bump using bmBump
    myBump = bmBump(bump_ind, abs(bump_ind[0]))
    # bmBump returns a 2-D array with a single row; take the first row
    myBump = myBump[0, :half_bump_width]

    # Apply the bump to the signal
    y = m.copy()
    y[ind_1 - 1 : ind_3] = myBump
    y[ind_4 : ind_2 + 1] = np.flip(myBump)

    return y
