# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np


def bmVarargin_cLineMask(inMask, nLine):
    """
    Generate a line mask based on the input mask and number of lines.

    Parameters
    ----------
    inMask : np.ndarray
        Input mask.
    nLine : int
        Number of lines to generate the mask for.

    Returns
    -------
    outMask : np.ndarray
        Generated line mask.
    """
    # The MATLAB code checks if the input mask is empty.
    # Here we replicate that logic: if the array has any elements, use it;
    # otherwise return a row of True of length nLine.
    if inMask is not None and getattr(inMask, "size", 0) > 0:
        return inMask
    else:
        return np.ones((1, nLine), dtype=bool)
