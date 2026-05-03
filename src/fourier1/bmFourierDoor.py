from __future__ import annotations

import numpy as np
from third_part.matlab_compat.matlab_native import permute
from src.arrayUtility.bmBlockReshape import bmBlockReshape


def bmFourierDoor(argK, argEdge, varargin):
    """
    Compute the Fourier door function.

    Parameters
    ----------
    argK : np.ndarray
        Input array.
    argEdge : list or float
        Edge parameter.
    varargin : list, optional
        Additional arguments.

    Returns
    -------
    np.ndarray
        Output array.
    """
    # a = 0;  (MATLAB default)
    # Parse edge argument
    if isinstance(argEdge, (list, tuple)):
        if len(argEdge) == 1:
            a = argEdge[0]
        else:
            raise ValueError("Wrong list of arguments.")
    else:
        a = argEdge
    # a <= 0 check
    if a <= 0:
        raise ValueError("Wrong list of arguments.")

    # Size check for argK: must be 1D or 2D with one row/column
    if argK.ndim > 1 and argK.shape[0] != 1 and argK.shape[1] != 1:
        raise ValueError("Wrong list of arguments")

    # myCenter from varargin
    myCenter = varargin[0] if varargin else 0

    # Machine epsilon
    myMachineEpsilon = 2 * np.finfo(float).eps

    # Permute if necessary to ensure a 1-D row vector
    if argK.ndim == 1 or argK.shape[0] == 1:
        k = argK if argK.ndim == 1 else argK[0]
    else:
        # swap first two dimensions
        k = permute(argK, (1, 0))
    k_size = np.shape(k)
    # Reshape to 1 x N
    k0 = bmBlockReshape(k, [1, -1])

    # Compute the sinc term
    myX = np.sin(np.pi * k0[0, :] * a) / (np.pi * k0[0, :])
    # Handle near-zero division
    myX[np.abs(k0[0, :]) < myMachineEpsilon] = a

    # Phase shift if myCenter is non-zero
    if not np.isclose(myCenter, 0):
        myX *= np.exp(1j * 2 * np.pi * myCenter * k0[0, :])

    # Reshape to original shape
    out = myX.reshape(argK.shape)

    return out
