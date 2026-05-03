from __future__ import annotations

import numpy as np
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmIsColShape import bmIsColShape
from src.arrayUtility.bmIsBlockShape import bmIsBlockShape


def bmMIP(y, N_u):
    """
    Compute the Maximum Intensity Projection (MIP) of the input data.

    Parameters
    ----------
    y : array_like
        Input data array. May be in block or column format.
    N_u : Sequence[int]
        Size of one channel in ``y``. Kept for API compatibility.

    Returns
    -------
    ndarray
        The MIP of ``y`` with the channel dimension removed.
    """
    # Convert to NumPy array
    y_arr = np.asarray(y)

    # Convert to column format: channels are the second dimension
    c = bmColReshape(y_arr, N_u)

    # Compute MIP: maximum absolute value across channels (axis 1)
    a = np.max(np.abs(c), axis=1)

    # Squeeze to remove any singleton dimensions
    a = np.squeeze(a)

    # Reshape back to original format depending on input shape
    if bmIsColShape(y_arr, N_u):
        a = bmColReshape(a, N_u)
    elif bmIsBlockShape(y_arr, N_u):
        a = bmBlockReshape(a, N_u)

    return a
