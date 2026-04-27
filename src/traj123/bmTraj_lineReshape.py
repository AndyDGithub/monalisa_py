import numpy as np
from src.traj123.bmTraj_nLine import bmTraj_nLine


def bmTraj_lineReshape(t, *varargin):
    imDim = t.shape[0]
    nLine, N, isN_integer, _ = bmTraj_nLine(t)
    if not isN_integer:
        raise ValueError("The size of traj is not convertible to [imDim, N, nLine]")

    N = int(round(N))
    # Use Fortran order to match MATLAB and bmPointReshape convention.
    out = t.reshape(imDim, N, nLine, order='F')

    if varargin:
        temp = varargin[0]
        nCh = temp.shape[0]
        return out, temp.reshape(nCh, N, nLine, order='F')

    return out
