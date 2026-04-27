import numpy as np


def bmIsScalar(x):
    if isinstance(x, (list, tuple)):
        return False
    return np.asarray(x).size == 1
