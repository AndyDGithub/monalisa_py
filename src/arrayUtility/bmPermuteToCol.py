import numpy as np
from src.varargin.bmVarargin import bmVarargin


def bmPermuteToCol(y, *varargin):
    argSize = bmVarargin(varargin)

    if isinstance(y, list):
        return [bmPermuteToCol(item, *([argSize] if argSize else [])) for item in y]
    if isinstance(y, np.ndarray) and y.dtype == object:
        out = np.empty_like(y)
        for i, item in enumerate(y.ravel()):
            out.ravel()[i] = bmPermuteToCol(item, *([argSize] if argSize else []))
        return out

    y = np.asarray(y)
    if y.size == 0:
        return np.array([])

    if argSize is None or (isinstance(argSize, (list, np.ndarray)) and len(np.asarray(argSize).ravel()) == 0):
        nCh = y.shape[0]
        nPt = y.size // nCh
    else:
        nPt = int(np.prod(np.asarray(argSize).ravel()))
        nCh = y.size // nPt

    return y.reshape(nCh, nPt).T
