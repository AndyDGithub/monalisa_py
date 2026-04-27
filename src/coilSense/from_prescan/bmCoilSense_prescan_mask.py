import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.imDisp.bmImage import bmImage
from src.image123.bmImClose import bmImClose
from src.image123.bmImOpen import bmImOpen
from src.image123.bmImShiftList import bmImShiftList
from src.imageN.bmMIP import bmMIP
from src.imageN.bmRMS import bmRMS

from src.varargin.bmVarargin import bmVarargin


def bmCoilSense_prescan_mask(x_body, n_u, varargin):
    colorMax = 100

    [x_min, x_max, y_min, y_max, z_min, z_max, th_RMS, th_MIP, open_size, close_size, display_flag] = bmVarargin(varargin)
    n_u = n_u.flatten()
    imDim = len(n_u)

    nCh_body = x_body.shape[0] // np.prod(n_u)

    x_body = np.abs(bmColReshape(x_body, n_u))
    for i in range(nCh_body):
        x_body[:, i] /= np.max(x_body[:, i])

    x = x_body.copy()
    x = bmBlockReshape(x, n_u)

    myRMS = bmRMS(x, n_u)
    myMIP = bmMIP(x, n_u)

    myRMS = colorMax * (myRMS - np.min(myRMS)) / np.max(myRMS)
    myMIP = colorMax * (myMIP - np.min(myMIP)) / np.max(myMIP)

    nPix = myRMS.size

    n_RMS = np.zeros((1, colorMax))
    n_MIP = np.zeros((1, colorMax))

    for i in range(colorMax):
        n_RMS[0, i] = np.sum(myRMS > i) / nPix
        n_MIP[0, i] = np.sum(myMIP > i) / nPix

    if display_flag:
        import matplotlib.pyplot as plt

        plt.figure()
        plt.plot(n_RMS[0], '.', label='RMS')
        plt.plot(n_MIP[0], '.', label='MIP')
        bmImage(myRMS, title='RMS')
        bmImage(myMIP, title='MIP')

    m = np.ones(myRMS.shape, dtype=bool)

    if not (th_RMS is None and th_MIP is None):
        if not (th_RMS is None):
            m &= myRMS > th_RMS
        if not (th_MIP is None):
            m &= myMIP > th_MIP

    if imDim == 1:
        if not (x_min is None or x_max is None):
            m[0:x_min, :] = False
            m[x_max:, :] = False
    elif imDim == 2:
        if not (x_min is None or x_max is None):
            m[0:x_min, :] = False
            m[x_max:, :] = False
        if not (y_min is None or y_max is None):
            m[:, 0:y_min] = False
            m[:, y_max:] = False
    elif imDim == 3:
        if not (x_min is None or x_max is None):
            if x_min > 1:
                m[:x_min - 1, :, :] = False
            if x_max < n_u[0]:
                m[x_max:, :, :] = False
        if not (y_min is None or y_max is None):
            if y_min > 1:
                m[:, :y_min - 1, :] = False
            if y_max < n_u[1]:
                m[:, y_max:, :] = False
        if not (z_min is None or z_max is None):
            if z_min > 1:
                m[:, :, :z_min] = False
            if z_max < n_u[2]:
                m[:, :, z_max:] = False

    if not (open_size is None) and open_size > 0:
        m = bmImOpen(m, bmImShiftList(["sphere", str(imDim)], open_size, 0))
    if not (close_size is None) and close_size > 0:
        m = bmImClose(m, bmImShiftList(["sphere", str(imDim)], close_size, 0))

    if np.sum(m == False) > 0:
        temp_im = m * myRMS
        temp_im = np.concatenate((temp_im / np.max(np.abs(temp_im)), m), axis=1)

        if display_flag:
            bmImage(temp_im)

    return bmBlockReshape(m, n_u)
