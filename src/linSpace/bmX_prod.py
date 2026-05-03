# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np


def bmX_prod(x1, x2, d_u):
    """
    Compute the inner product of two 2-D complex arrays weighted by the spa
spatial increments.

    Parameters
    ----------
    x1 : np.ndarray
        First complex array.
    x2 : np.ndarray
        Second complex array.
    d_u : array_like
        Spatial increments.

    Returns
    -------
    p : np.ndarray
        Resulting vector.

    Notes
    -----
    This function is for 2Dim arrays only.
    Both arrays must have the same size.
    """
    if x1.ndim > 2:
        raise ValueError("This function is for 2Dim arrays only.")
    if x1.shape != x2.shape:
        raise ValueError("Both arrays must have the same size.")

    dV = np.prod(d_u)
    if x1.shape[0] > x1.shape[1]:
        p = np.sum(np.conj(x1) * (x2 * dV), axis=0)
    else:
        p = np.sum(np.conj(x1) * (x2 * dV), axis=1)

    return p
