import numpy as np

def bmNormalVector2(ex):
    ey = np.zeros((2, 1))
    ey[0] = ex[1]
    ey[1] = -ex[0]
    return ey
