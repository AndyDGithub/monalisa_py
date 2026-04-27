import numpy as np

def bmVarargin_eLineMask(inMask, nLine):
    if not(np.any(inMask)):
        outMask = np.zeros((1, nLine), dtype=bool)
    else:
        outMask = inMask

    return outMask
