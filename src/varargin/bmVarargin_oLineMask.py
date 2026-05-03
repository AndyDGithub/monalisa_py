import numpy as np

def bmVarargin_oLineMask(inMask, nLine):
    """Generate a line mask based on the input mask and number of lines.

    This function checks if the input mask is empty. If it is, it creates a
a mask
    with all elements set to True. Otherwise, it returns the input mask unc
unchanged.

    Parameters:
        inMask (np.ndarray): The input mask as a boolean array.
        nLine (int): The number of lines for the output mask if inMask is e
empty.

    Returns:
        np.ndarray: The resulting line mask.
    """
    if not np.any(inMask):
        outMask = np.ones((1, nLine), dtype=bool)
    else:
        outMask = inMask
    return outMask

from src.geom123 import bmTraj
