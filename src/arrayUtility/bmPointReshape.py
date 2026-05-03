from __future__ import annotations
import numpy as np
from third_part.matlab_compat.matlab_native import isempty, size
from porting.lib.utils import ndims
from src.varargin.bmVarargin import bmVarargin

def bmPointReshape(t, varargin):
    """Strict deterministic baseline port from MATLAB."""
    argSize = bmVarargin(*varargs)

    if isinstance(t, list):
        out = [bmPointReshape(item, argSize) for item in t]
        return out

    if ndims(t) == 2:
        if (t.shape[0] == 1) or (t.shape[1] == 1):
            return t.flatten()

    argSize = bmVarargin(*varargs)
    argSize = np.array(argSize).reshape(-1)

    nCh = size(t, 0) if isempty(argSize) else int(argSize[0])
    nPt = size(t, 0) // nCh

    return t.reshape(nCh, nPt)
