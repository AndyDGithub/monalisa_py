import numpy as np
from src.interp1.bmInterp1 import bmInterp1


def bmMriPhi_fromSI_imNav(
    rmsSI,
    _,
    nSeg,
    __,
    ind_shot_min,
    ind_shot_max,
    ___,
    ____,
    ind_imNav_min,
    ind_imNav_max,
    _____,
):
    """
    Compute the navigation image (imNav) from the signal intensity (rmsSI).

    Parameters
    ----------
    rmsSI : np.ndarray
        Input signal intensity matrix.
    _ : Any
        Unused placeholder.
    nSeg : int
        Segmentation factor used for interpolation.
    __ : Any
        Unused placeholder.
    ind_shot_min : int
        Minimum shot index (MATLAB 1-based inclusive).
    ind_shot_max : int
        Maximum shot index (MATLAB 1-based inclusive).
    ___ : Any
        Unused placeholder.
    ____ : Any
        Unused placeholder.
    ind_imNav_min : int
        Minimum imNav index (MATLAB 1-based inclusive).
    ind_imNav_max : int
        Maximum imNav index (MATLAB 1-based inclusive).
    _____ : Any
        Unused placeholder.

    Returns
    -------
    imNav : np.ndarray
        Normalized navigation image.
    """
    # Convert MATLAB 1-based inclusive indices to Python 0-based exclusive slices
    rmsSI_slice = rmsSI[ind_imNav_min:ind_imNav_max + 1, ind_shot_min:ind_shot_max + 1]

    mySize_1, mySize_2 = rmsSI_slice.shape
    mySize_2_interp = mySize_2 * nSeg + 1

    # t_interp and t_interpolant (MATLAB indices start at 1)
    t_interp = np.arange(1, mySize_2_interp + 1)
    t_interpolant = t_interp[::nSeg]

    # Append the second-to-last column to rmsSI_slice
    rmsSI_cat = np.concatenate([rmsSI_slice, rmsSI_slice[:, -2:-1]], axis=1)

    # Interpolate each row
    imNav = np.zeros((mySize_1, mySize_2_interp))
    for i in range(mySize_1):
        imNav[i, :] = bmInterp1(t_interpolant, rmsSI_cat[i, :], t_interp)

    # Remove the last column
    imNav = imNav[:, :-1]

    # Normalize
    imNav -= imNav.min()
    max_val = imNav.max()
    if max_val != 0:
        imNav /= max_val

    return imNav
