import numpy as np

def bmVarargin_oLineMask(inMask, nLine):
    if not np.any(inMask):
        outMask = np.ones((1, nLine), dtype=bool)
    else:
        outMask = inMask
    return outMask
