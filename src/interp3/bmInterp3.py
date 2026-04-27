import numpy as np
from scipy.interpolate import interpn

def bmInterp3(argIm, argMethod, varargin):
    argSize = np.shape(argIm)
    argSize = argSize.ravel().T
    if len(argSize) != 3:
        raise ValueError("In bmInterp3 : the input image must be 3 dimensional.")

    argSize_1 = argSize[0]
    argSize_2 = argSize[1]
    argSize_3 = argSize[2]

    if len(varargin) in [5, 6]:
        x2 = varargin[1].ravel()
        y2 = varargin[2].ravel()
        z2 = varargin[3].ravel()
        out = interpn(argIm, x2, y2, z2, argMethod)

    elif len(varargin) in [8, 9]:
        x = varargin[1].reshape([argSize_1, argSize_2, argSize_3])
        y = varargin[2].reshape([argSize_1, argSize_2, argSize_3])
        z = varargin[3].reshape([argSize_1, argSize_2, argSize_3])
        x2 = varargin[4].ravel()
        y2 = varargin[5].ravel()
        z2 = varargin[6].ravel()

        out = interpn(x, y, z, argIm, x2, y2, z2, argMethod)

    if len(varargin) == 9 and varargin[-1] == 'reshape':
        out = np.reshape(out, [argSize_1, argSize_2, argSize_3])

    out[np.isnan(out)] = 0

    if isinstance(argIm, np.float32):
        out = np.float32(out)
    elif isinstance(argIm, np.float64):
        out = np.float64(out)

    return out
