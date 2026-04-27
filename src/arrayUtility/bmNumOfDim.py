import numpy as np


def bmNumOfDim(a):
    a = np.asarray(a)
    s = np.array(a.shape) if a.ndim > 0 else np.array([1, 1])
    if s.size == 0:
        s = np.array([1, 1])
    elif s.size == 1:
        s = np.array([1, s[0]])
    n = max(a.ndim, 2)
    if n == 2:
        if s.min() == 0:
            n = 0
        elif s.min() == 1:
            n = 1
        else:
            n = 2
    return n
