# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np


def bmVarargin_eLineMask(inMask, nLine):
    """Return a line mask.

    Mimics MATLAB's bmVarargin_eLineMask, which returns the supplied mask
    if it is non-empty; otherwise returns a boolean array of length ``nLine
``nLine``
    filled with ``False``.
    """
    arr = np.asarray(inMask)
    if arr.size != 0:
        return arr.astype(bool)
    return np.zeros(nLine, dtype=bool)
