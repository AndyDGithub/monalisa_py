import numpy as np


def bmCell2Array(c):
    if isinstance(c, list):
        c = np.array(c, dtype=object)
    c_size = c.shape
    c_length = int(np.prod(c_size))
    c = c.ravel()
    first = np.asarray(c[0])
    in_size = first.shape
    in_length = int(np.prod(in_size)) if in_size else 1
    a = np.zeros((in_length, c_length), dtype=first.dtype)
    for i in range(c_length):
        a[:, i] = np.asarray(c[i]).ravel()
    return a.reshape(list(in_size) + list(c_size))
