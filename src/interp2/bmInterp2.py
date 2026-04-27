import numpy as np
from scipy.interpolate import interpn

def bmInterp2(argIm, argMethod, varargin):
    argSize = np.shape(argIm)
    argSize = argSize.ravel().T

    if len(argSize) > 3:
        raise ValueError("In bmInterp2 : the input image must be 2 or 3 dimensional.")

    if len(argSize) == 3:
        argSize_1, argSize_2, argSize_3 = argSize
    else:
        argSize_1, argSize_2 = argSize[:2]
        argSize_3 = 1

    if len(varargin) in [4, 5]:
        x2 = varargin[1].ravel()
        y2 = varargin[2].ravel()
        out = np.zeros((np.shape(x2)[0], argSize_3))

        for i in range(argSize_3):
            out[:, i] = interpn(argIm[:, :, i], x2, y2, argMethod)

    elif len(varargin) in [6, 7]:
        x = varargin[1].reshape([argSize_1, argSize_2])
        y = varargin[2].reshape([argSize_1, argSize_2])
        x2 = varargin[3].ravel()
        y2 = varargin[4].ravel()
        out = np.zeros((np.shape(x2)[0], argSize_3))

        for i in range(argSize_3):
            out[:, i] = interpn(x, y, argIm[:, :, i], x2, y2, argMethod)

    if len(varargin) == 7 and varargin[-1] == 'reshape':
        out = out.reshape([argSize_1, argSize_2, argSize_3])

    out[np.isnan(out)] = 0

    if isinstance(argIm, np.ndarray) and argIm.dtype == np.dtype('single'):
        out = out.astype(np.dtype('float32'))
    elif isinstance(argIm, np.ndarray) and argIm.dtype == np.dtype('double'):
        out = out.astype(np.dtype('float64'))

    return out
