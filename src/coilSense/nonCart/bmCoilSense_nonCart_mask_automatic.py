from __future__ import annotations
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha


def bmCoilSense_nonCart_mask_automatic(y, Gn, autoFlag, varargin):
    """Create a mask automatically for regridded non-Cartesian data.

    Creates a mask for the regridded data calculated with Gn*y. If
    thresholds or borders are not provided they are determined automatically.
    Only works for 3D data at the moment (X, Y, Z and channels).

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
    autoFlag (bool): Automatically decide thresholds and borders if True.
    varargin[0]: Threshold for RMS value (auto-computed if None).
    varargin[1]: Threshold for MIP value (auto-computed if None).
    varargin[2]: borders array of shape (imDim, 2): [[xMin,xMax],[yMin,yMax],[zMin,zMax]]
                 (auto-computed if None).
    varargin[3]: open_size for morphological opening.
    varargin[4]: close_size for morphological closing.

    Returns:
    m (array): Mask in block format.
    """
    colorMax = 100

    # Parse optional arguments
    args = list(varargin) if varargin is not None else []

    def _get(i):
        return args[i] if i < len(args) else None

    th_RMS    = _get(0)
    th_MIP    = _get(1)
    borders   = _get(2)   # shape (imDim, 2): [[xMin,xMax],[yMin,yMax],[zMin,zMax]]
    open_size  = _get(3)
    close_size = _get(4)

    N_u     = np.asarray(Gn.N_u, dtype=float).ravel()
    imDim   = len(N_u)
    N_u_int = N_u.astype(int).tolist()

    # Grid to image space
    x_im = bmBlockReshape(bmNasha(y, Gn, N_u), N_u_int)

    # Compute RMS across channels
    try:
        from src.image123.bmRMS import bmRMS
        myRMS = bmRMS(x_im, N_u_int)
    except Exception:
        myRMS = np.sqrt(np.mean(np.abs(x_im) ** 2, axis=-1))

    # Compute MIP across channels
    try:
        from src.image123.bmMIP import bmMIP
        myMIP = bmMIP(x_im, N_u_int)
    except Exception:
        myMIP = np.max(np.abs(x_im), axis=-1)

    # Normalize RMS to [0, colorMax]
    mn_rms = np.min(myRMS.ravel())
    mx_rms = np.max(myRMS.ravel())
    myRMS = colorMax * (myRMS - mn_rms) / mx_rms if mx_rms > mn_rms else np.zeros_like(myRMS)

    # Normalize MIP to [0, colorMax]
    mn_mip = np.min(myMIP.ravel())
    mx_mip = np.max(myMIP.ravel())
    myMIP = colorMax * (myMIP - mn_mip) / mx_mip if mx_mip > mn_mip else np.zeros_like(myMIP)

    # Automatic threshold computation
    if th_RMS is None or th_MIP is None:
        nonzero_rms = myRMS.ravel()[myRMS.ravel() > 0]
        auto_th_rms = float(np.percentile(nonzero_rms, 10)) if len(nonzero_rms) > 0 else 0.0
        nonzero_mip = myMIP.ravel()[myMIP.ravel() > 0]
        auto_th_mip = float(np.percentile(nonzero_mip, 10)) if len(nonzero_mip) > 0 else 0.0
        if th_RMS is None:
            th_RMS = auto_th_rms
        if th_MIP is None:
            th_MIP = auto_th_mip

    # Automatic border detection
    if borders is None:
        tempRMS = myRMS.copy()
        tempRMS[tempRMS <= th_RMS] = 0
        tempMIP = myMIP.copy()
        tempMIP[tempMIP <= th_MIP] = 0
        borders = np.zeros((imDim, 2), dtype=int)
        for d in range(imDim):
            other_axes = tuple(i for i in range(imDim) if i != d)
            axis_sum = np.sum(tempRMS + tempMIP, axis=other_axes)
            nonz = np.where(axis_sum > 0)[0]
            borders[d, 0] = int(nonz[0]) + 1 if len(nonz) > 0 else 1
            borders[d, 1] = int(nonz[-1]) + 1 if len(nonz) > 0 else N_u_int[d]

    # Optional display before masking
    if not autoFlag:
        try:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.title('RMS')
            plt.imshow(myRMS.reshape(N_u_int[0], -1) if imDim >= 2 else myRMS.ravel().reshape(1, -1))
            plt.figure()
            plt.title('MIP')
            plt.imshow(myMIP.reshape(N_u_int[0], -1) if imDim >= 2 else myMIP.ravel().reshape(1, -1))
            plt.show()
        except Exception:
            pass

    # Build mask using thresholds
    m = (myRMS > th_RMS) & (myMIP > th_MIP)

    # Apply borders (3D only, matching MATLAB logic)
    if imDim == 3 and borders is not None:
        borders = np.asarray(borders)
        if borders[0, 0] > 1:
            m[:borders[0, 0] - 1, :, :] = False
        if borders[0, 1] < N_u_int[0]:
            m[borders[0, 1]:, :, :] = False
        if borders[1, 0] > 1:
            m[:, :borders[1, 0] - 1, :] = False
        if borders[1, 1] < N_u_int[1]:
            m[:, borders[1, 1]:, :] = False
        if borders[2, 0] > 1:
            m[:, :, :borders[2, 0]] = False
        if borders[2, 1] < N_u_int[2]:
            m[:, :, borders[2, 1]:] = False

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

    # Optional display of result
    if not autoFlag and np.sum(~m) > 0:
        try:
            import matplotlib.pyplot as plt
            temp_im = m.astype(float) * myRMS
            mx_temp = np.max(np.abs(temp_im.ravel()))
            if mx_temp > 0:
                temp_im = temp_im / mx_temp
            plt.figure()
            plt.title('Masked RMS | Mask')
            plt.imshow(np.concatenate([temp_im, m.astype(float)], axis=1) if imDim == 2 else temp_im.reshape(N_u_int[0], -1))
            plt.show()
        except Exception:
            pass

    # Reshape mask to block format
    m = bmBlockReshape(m.astype(float), N_u_int).astype(bool)
    return m
