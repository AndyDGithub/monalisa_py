from __future__ import annotations

import numpy as np
from typing import Any

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.image123.bmImClose import bmImClose
from src.image123.bmImOpen import bmImOpen
from src.image123.bmImShiftList import bmImShiftList
from src.imDisp.bmImage import bmImage
from src.varargin.bmVarargin import bmVarargin
from src.imageN.bmMIP import bmMIP
from src.imageN.bmRMS import bmRMS


def bmCoilSense_prescan_mask(
    x_body: np.ndarray,
    n_u: Any,
    *varargin: Any,
) -> np.ndarray:
    """
    Generate a mask from a body coil prescan image.

    Parameters
    ----------
    x_body : np.ndarray
        The body coil prescan image data.
    n_u : array-like
        The spatial size of each channel (e.g., [96, 96] or [64, 56, 32]).
    *varargin : Any
        Optional parameters passed via bmVarargin. Expected to return the
        following variables in order:
            x_min, x_max, y_min, y_max, z_min, z_max,
            th_RMS, th_MIP, open_size, close_size, display_flag
    Returns
    -------
    np.ndarray
        Boolean mask of the same shape as the input image.
    """
    # Default parameters
    colorMax = 100

    # Parse optional arguments
    (
        x_min,
        x_max,
        y_min,
        y_max,
        z_min,
        z_max,
        th_RMS,
        th_MIP,
        open_size,
        close_size,
        display_flag,
    ) = bmVarargin(*varargin)

    # Normalise n_u to a 1-D array of ints
    n_u_arr = np.asarray(n_u, dtype=int).reshape(-1)
    imDim = n_u_arr.size

    # Compute number of channels
    nCh_body = x_body.size // int(np.prod(n_u_arr))

    # Reshape body image into (prod(n_u), nCh_body)
    x_body = np.abs(np.asarray(x_body, dtype=np.float32))
    x_body = x_body.reshape((int(np.prod(n_u_arr)), -1))
    # Normalize each channel
    max_vals = x_body.max(axis=0)
    max_vals[max_vals == 0] = 1
    x_body = x_body / max_vals

    # Re-arrange into spatial dimensions
    x = bmBlockReshape(x_body, n_u_arr)

    # Compute RMS and MIP
    myRMS = bmRMS(x, n_u_arr)
    myMIP = bmMIP(x, n_u_arr)

    # Scale to [0, colorMax]
    def _scale(arr: np.ndarray) -> np.ndarray:
        mn, mx = arr.min(), arr.max()
        if mx == mn:
            return np.zeros_like(arr)
        return colorMax * (arr - mn) / (mx - mn)

    myRMS = _scale(myRMS)
    myMIP = _scale(myMIP)

    nPix = myRMS.size
    n_RMS = np.zeros(colorMax, dtype=float)
    n_MIP = np.zeros(colorMax, dtype=float)

    for i in range(colorMax):
        n_RMS[i] = np.sum(myRMS > i) / nPix
        n_MIP[i] = np.sum(myMIP > i) / nPix

    # Optional display
    if display_flag:
        import matplotlib.pyplot as plt

        plt.figure()
        plt.plot(n_RMS, ".-")
        plt.plot(n_MIP, ".-")
        bmImage(myRMS)
        plt.title("RMS")
        bmImage(myMIP)
        plt.title("MIP")

    # Initialise mask
    m = np.ones_like(myRMS, dtype=bool)

    # Threshold logic
    if th_RMS is not None and th_MIP is None:
        m = (myRMS > th_RMS) & (myMIP > th_RMS)
    elif th_RMS is None and th_MIP is not None:
        m = (myRMS > th_MIP) & (myMIP > th_MIP)
    elif th_RMS is not None and th_MIP is not None:
        m = (myRMS > th_RMS) & (myMIP > th_MIP)

    # Spatial exclusions based on imDim
    if imDim == 1:
        if x_min is not None and x_max is not None:
            m[0:x_min, :] = False
            m[x_max - 1 :, :] = False
    elif imDim == 2:
        if x_min is not None and x_max is not None:
            m[0:x_min, :] = False
            m[x_max - 1 :, :] = False
        if y_min is not None and y_max is not None:
            m[:, 0:y_min] = False
            m[:, y_max - 1 :] = False
    elif imDim == 3:
        if x_min is not None and x_max is not None:
            if x_min > 1:
                m[0:x_min - 1, :, :] = False
            if x_max < n_u_arr[0]:
                m[x_max :, :, :] = False
        if y_min is not None and y_max is not None:
            if y_min > 1:
                m[:, 0:y_min - 1, :] = False
            if y_max < n_u_arr[1]:
                m[:, y_max :, :] = False
        if z_min is not None and z_max is not None:
            if z_min > 1:
                m[:, :, 0:z_min] = False
            if z_max < n_u_arr[2]:
                m[:, :, z_max :] = False

    # Morphological operations
    if open_size is not None and open_size > 0:
        m = bmImOpen(
            m,
            bmImShiftList(["sphere", str(imDim)], open_size, 0),
        )
    if close_size is not None and close_size > 0:
        m = bmImClose(
            m,
            bmImShiftList(["sphere", str(imDim)], close_size, 0),
        )

    # Final check for display
    if not m.any():
        temp_im = m.astype(float) * myRMS
        max_abs = np.max(np.abs(temp_im))
        if max_abs == 0:
            temp_im = np.zeros_like(temp_im)
        else:
            temp_im = temp_im / max_abs
        temp_im = np.concatenate((temp_im, m.astype(float)), axis=1)
        if display_flag:
            bmImage(temp_im)

    # Reshape mask back to spatial dimensions
    m = bmBlockReshape(m, n_u_arr)

    return m

if __name__ == "__main__":
    # Example test harness (optional)
    x = np.random.rand(64 * 56 * 32, 1)
    mask = bmCoilSense_prescan_mask(x, [64, 56, 32])
    print(mask.shape, mask.dtype)
