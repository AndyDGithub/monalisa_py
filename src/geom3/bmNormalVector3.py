import numpy as np
from src.arrayUtility import bmBlockReshape  # Importing the missing module

def bmNormalVector3(ez):
    ez = ez.ravel()
    ez /= np.sqrt(np.sum(ez**2))

    ey, myPerm = bmBlockReshape(ez, (3,))
    temp = ey[2]
    ey[2] = ey[1]
    ey[1] = -temp
    ey[0] = 0

    ey /= np.sqrt(np.sum(ey**2))
    ey = ey[myPerm[::-1]]

    ex = np.cross(ey, ez)
    ex = ex.ravel()

    if len(ex) > 1:
        varargout = [ex]
    else:
        varargout = ex

    return (ey, varargout)
