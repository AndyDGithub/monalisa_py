from __future__ import annotations
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha


def bmCoilSense_nonCart_mask(y, Gn, varargin):
    """Create a mask for regridded non-Cartesian data.

    The mask excludes pixels outside the ROI and below threshold values
    for RMS and MIP images.

    Authors:
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023

    Contributors:
    Dominik Helbing (Documentation & Comments)
    MattechLab 2024

    Parameters:
    y (array): Raw data to be gridded onto the grid defined by Gn.
    Gn (bmSparseMat): Sparse Matrix defining the new uniform grid.
    varargin[0]: Lower boundary of x indices (ROI).
    varargin[1]: Upper boundary of x indices (ROI).
    varargin[2]: Lower boundary of y indices (ROI).
    varargin[3]: Upper boundary of y indices (ROI).
    varargin[4]: Lower boundary of z indices (ROI).
    varargin[5]: Upper boundary of z indices (ROI).
    varargin[6]: Threshold for RMS value.
    varargin[7]: Threshold for MIP value.
    varargin[8]: open_size for morphological opening.
    varargin[9]: close_size for morphological closing.
    varargin[10]: display_flag; display images if True.

    Returns:
    m (array): Mask in block format.
    """
    colorMax = 100

    # Parse optional arguments
    args = list(varargin) if varargin is not None else []

    def _get(i):
        return args[i] if i < len(args) else None

    x_min        = _get(0)
    x_max        = _get(1)
    y_min        = _get(2)
    y_max        = _get(3)
    z_min        = _get(4)
    z_max        = _get(5)
    th_RMS       = _get(6)
    th_MIP       = _get(7)
    open_size    = _get(8)
    close_size   = _get(9)
    display_flag = bool(_get(10)) if _get(10) is not None else False

    N_u     = np.asarray(Gn.N_u, dtype=float).ravel()
    imDim   = len(N_u)
    N_u_int = N_u.astype(int).tolist()

    # Grid to image space
    x_im = bmBlockReshape(bmNasha(y, Gn, N_u), N_u_int)

    # Compute RMS across channels
    try:
        from src.imageN.bmRMS import bmRMS
        myRMS = bmRMS(x_im, N_u_int)
    except Exception:
        myRMS = np.sqrt(np.mean(np.abs(x_im) ** 2, axis=-1))

    # Compute MIP across channels
    try:
        from src.imageN.bmMIP import bmMIP
        myMIP = bmMIP(x_im, N_u_int)
    except Exception:
        myMIP = np.max(np.abs(x_im), axis=-1)

    # Normalize RMS to [0, colorMax]
    mn_rms = np.min(myRMS.ravel())
    mx_rms = np.max(myRMS.ravel())
    if mx_rms > mn_rms:
        myRMS = colorMax * (myRMS - mn_rms) / mx_rms
    else:
        myRMS = np.zeros_like(myRMS)

    # Normalize MIP to [0, colorMax]
    mn_mip = np.min(myMIP.ravel())
    mx_mip = np.max(myMIP.ravel())
    if mx_mip > mn_mip:
        myMIP = colorMax * (myMIP - mn_mip) / mx_mip
    else:
        myMIP = np.zeros_like(myMIP)

    # Histogram: fraction of pixels above each integer value
    nPix  = myRMS.size
    n_RMS = np.array([np.sum(myRMS.ravel() > i) / nPix for i in range(colorMax)])
    n_MIP = np.array([np.sum(myMIP.ravel() > i) / nPix for i in range(colorMax)])

    # Optional display
    if display_flag:
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(n_RMS, '.-', label='RMS')
            ax.plot(n_MIP, '.-', label='MIP')
            ax.set_xlabel('X')
            ax.set_ylabel('Fraction above X')
            ax.legend()
            ax.set_title('Fraction of points having a value above X')
            plt.show()
        except Exception:
            pass

    # Build mask
    m = np.ones(myRMS.shape, dtype=bool)

    if th_RMS is not None and th_MIP is None:
        m = (myRMS > th_RMS) & (myMIP > th_RMS)
    elif th_RMS is None and th_MIP is not None:
        m = (myRMS > th_MIP) & (myMIP > th_MIP)
    elif th_RMS is not None and th_MIP is not None:
        m = (myRMS > th_RMS) & (myMIP > th_MIP)

    # Spatial crop
    if imDim == 1:
        if x_min is not None and x_max is not None:
            m[:x_min] = False
            m[x_max:] = False
    elif imDim == 2:
        if x_min is not None and x_max is not None:
            m[:x_min, :] = False
            m[x_max:, :] = False
        if y_min is not None and y_max is not None:
            m[:, :y_min] = False
            m[:, y_max:] = False
    elif imDim == 3:
        if x_min is not None and x_max is not None:
            if x_min > 1:
                m[:x_min - 1, :, :] = False
            if x_max < N_u_int[0]:
                m[x_max:, :, :] = False
        if y_min is not None and y_max is not None:
            if y_min > 1:
                m[:, :y_min - 1, :] = False
            if y_max < N_u_int[1]:
                m[:, y_max:, :] = False
        if z_min is not None and z_max is not None:
            if z_min > 1:
                m[:, :, :z_min] = False
            if z_max < N_u_int[2]:
                m[:, :, z_max:] = False

    # Morphological open/close
    try:
        from src.image123.bmImOpen import bmImOpen
        from src.image123.bmImClose import bmImClose
        from src.image123.bmImShiftList import bmImShiftList
        if open_size is not None and open_size > 0:
            m = bmImOpen(m, bmImShiftList(f'sphere{imDim}', open_size, 0))
        if close_size is not None and close_size > 0:
            m = bmImClose(m, bmImShiftList(f'sphere{imDim}', close_size, 0))
    except Exception:
        pass

    # Optional display of masked RMS
    if display_flag and np.sum(~m) > 0:
        try:
            import matplotlib.pyplot as plt
            temp_im = m.astype(float) * myRMS
            mx_temp = np.max(np.abs(temp_im.ravel()))
            if mx_temp > 0:
                temp_im = temp_im / mx_temp
            plt.figure()
            plt.imshow(np.concatenate([temp_im, m.astype(float)], axis=1) if imDim == 2 else temp_im.reshape(-1, temp_im.shape[-1]))
            plt.title('Masked RMS | Mask')
            plt.show()
        except Exception:
            pass

    # Reshape mask to block format
    m = bmBlockReshape(m.astype(float), N_u_int).astype(bool)
    return m
