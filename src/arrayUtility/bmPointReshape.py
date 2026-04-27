import numpy as np
from src.varargin.bmVarargin import bmVarargin


def bmPointReshape(t, *varargin):
    argSize = bmVarargin(varargin)

    if isinstance(t, list):
        return [bmPointReshape(item, *([argSize] if argSize else [])) for item in t]
    if isinstance(t, np.ndarray) and t.dtype == object:
        out = np.empty_like(t)
        for i, item in enumerate(t.ravel()):
            out.ravel()[i] = bmPointReshape(item, *([argSize] if argSize else []))
        return out

    t = np.asarray(t)

    # 1D vectors (row or column) -> return as 1D row
    if t.ndim <= 2 and (t.ndim == 1 or t.shape[0] == 1 or t.shape[1] == 1):
        return t.ravel()

    if argSize is None or (isinstance(argSize, (list, np.ndarray)) and len(np.asarray(argSize).ravel()) == 0):
        nCh = t.shape[0]
    else:
        nCh = int(np.asarray(argSize).ravel()[0])

    nPt = t.size // nCh
    # Use Fortran (column-major) order to match MATLAB reshape behaviour.
    # For 2D inputs this has no effect; for 3D+ it groups consecutive points
    # from the same spoke/line together (innermost dimension first).
    return t.reshape(nCh, nPt, order='F')
