from src.fourierN.bmDFT import bmDFT
from src.imageN.bmImDim import bmImDim
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape


def bmImDFT(argIm, varargin):
    nZero_x = []
    if len(varargin) > 0:
        nZero_x = varargin[0]
    nZero_y = []
    if len(varargin) > 1:
        nZero_y = varargin[1]
    nZero_z = []
    if len(varargin) > 2:
        nZero_z = varargin[2]

    kx = []
    ky = []
    kz = []
    myDim = bmImDim(argIm)

    if myDim == 1:
        Ff, kx = bmDFT(argIm, 1, nZero_x, 1)
    elif myDim == 2:
        Ff, kx = bmDFT(argIm, 1, nZero_x, 1)
        Ff, ky = bmDFT(Ff, 1, nZero_y, 2)
    elif myDim == 3:
        Ff, kx = bmDFT(argIm, 1, nZero_x, 1)
        Ff, ky = bmDFT(Ff, 1, nZero_y, 2)
        Ff, kz = bmDFT(Ff, 1, nZero_z, 3)

    kxyz = np.stack((kx, ky, kz), axis=-1)
    return Ff, (kx, ky, kz) if myDim < 4 else (kx, ky, kz, bmBlockReshape(kxyz, myDim))
