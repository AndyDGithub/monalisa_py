import numpy as np
from src.fourierN.bmIDF import bmIDF
from src.imageN.bmImDim import bmImDim


def bmImIDF(argIm, varargin):
    nZero_x = []
    if len(varargin) > 0:
        nZero_x = varargin[0]

    nZero_y = []
    if len(varargin) > 1:
        nZero_y = varargin[1]

    nZero_z = []
    if len(varargin) > 2:
        nZero_z = varargin[2]

    myDim = bmImDim(argIm)

    iFf = None
    if myDim == 1:
        iFf = bmIDF(argIm, 1, nZero_x, 1)
        iFf = iFf / np.shape(argIm, 1)
    elif myDim == 2:
        iFf = bmIDF(argIm, 1, nZero_x, 1)
        iFf = bmIDF(iFf, 1, nZero_y, 2)
        iFf = iFf / np.shape(argIm, 1)
        iFf = iFf / np.shape(argIm, 2)
    elif myDim == 3:
        iFf = bmIDF(argIm, 1, nZero_x, 1)
        iFf = bmIDF(iFf, 1, nZero_y, 2)
        iFf = bmIDF(iFf, 1, nZero_z, 3)
        iFf = iFf / np.shape(argIm, 1)
        iFf = iFf / np.shape(argIm, 2)
        iFf = iFf / np.shape(argIm, 3)
    else:
        raise ValueError("Unsupported dimension")

    return iFf
