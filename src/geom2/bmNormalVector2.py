# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np


def bmNormalVector2(ex):
    """Return a normal vector to the 2-element vector *ex*.

    The function follows the MATLAB implementation which returns a
    column vector ``ey`` with shape ``(2, 1)``.
    """
    ex_arr = np.asarray(ex).reshape(-1)
    if ex_arr.size != 2:
        raise ValueError("ex must be a 2-element vector")

    ey = np.zeros((2, 1))
    ey[0, 0] = ex_arr[1]
    ey[1, 0] = -ex_arr[0]
    return ey
