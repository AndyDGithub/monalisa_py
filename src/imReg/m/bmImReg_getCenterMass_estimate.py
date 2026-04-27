import numpy as np
from typing import Tuple

from src.arrayUtility.bmCol import bmCol
from src.image123.bmImGrid import bmImGrid
from src.mask123.bmElipsoidMask import bmElipsoidMask

def bmImReg_getCenterMass_estimate(argIm: np.ndarray, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, varargin: list) -> Tuple[np.ndarray, np.ndarray]:
    myOption = bmVarargin(varargin)
    if not myOption:
        myOption = 'normal'

    n_u  = np.array(argIm.shape)
    n_u  = n_u.flatten()
    imDim   = len(n_u)
    argIm   = np.single(np.abs(argIm))

    if imDim == 2:
        nx, ny = n_u[:2]
    elif imDim == 3:
        nx, ny, nz = n_u

    X, Y, Z = bmImGrid(n_u, X, Y, Z)

    if myOption == 'normal':

        m = bmElipsoidMask(argIm.shape, np.array(argIm.shape)/2)
        argIm   = argIm * m
        im_sum  = np.sum(argIm)
        if im_sum == 0:
            im_sum = 1

        if imDim == 2:
            c_x = np.sum(X * argIm) / im_sum
            c_y = np.sum(Y * argIm) / im_sum
            c = np.array([c_x, c_y])
        elif imDim == 3:
            c_x = np.sum(X * argIm) / im_sum
            c_y = np.sum(Y * argIm) / im_sum
            c_z = np.sum(Z * argIm) / im_sum
            c = np.array([c_x, c_y, c_z])

    elif myOption == 'extended':

        imSupport = np.single(np.abs(argIm) > 0)

        if imDim == 2:
            R2 = (X - (nx/2 + 1))**2 + (Y - (ny/2 + 1))**2
        elif imDim == 3:
            R2 = (X - (nx/2 + 1))**2 + (Y - (ny/2 + 1))**2 + (Z - (nz/2 + 1))**2

        if imDim == 2:
            c       = np.zeros((imDim, 4))
            d       = np.zeros(1, 4)
            s       = np.zeros((4, imDim))

            sx = int((nx - 1)/2) + 1
            sy = int((ny - 1)/2) + 1

            s[0, :] = [0,     0]
            s[1, :] = [sx,    0]
            s[2, :] = [0,    sy]
            s[3, :] = [sx,   sy]

        elif imDim == 3:
            c       = np.zeros((imDim, 8))
            d       = np.zeros(1, 8)
            s       = np.zeros((8, imDim))

            sx = int((nx - 1)/2) + 1
            sy = int((ny - 1)/2) + 1
            sz = int((nz - 1)/2) + 1

            s[0, :] = [0,      0,       0]
            s[1, :] = [sx,     0,       0]
            s[2, :] = [0,      sy,      0]
            s[3, :] = [0,      0,     sz]
            s[4, :] = [sx,     sy,      0]
            s[5, :] = [0,      sy,     sz]
            s[6, :] = [sx,     0,      sz]
            s[7, :] = [sx,     sy,     sz]

        for i in range(len(s)):
            myIm                = np.roll(argIm, s[i, :])
            c_temp, d_temp       = private_get_c_d(myIm, m, X, Y, Z, R2, imDim)
            c[:, i]             = c_temp
            d[0, i]             = d_temp

        myInd = np.argmin(d)
        c               = c[:, myInd]
        s               = bmCol(  s[myInd, :]  )

        for i in range(imDim):
            c[i, 0] = (c[i, 0] - s[i, 0] - 1) % n_u[i] + 1

    return c, d
