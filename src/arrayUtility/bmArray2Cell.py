import numpy as np


def bmArray2Cell(a, N_u):
    nDim_array = int(np.size(N_u))
    a = np.asarray(a)
    a_size = a.shape
    in_size = a_size[:nDim_array]
    in_length = int(np.prod(in_size)) if in_size else 1
    c_size = a_size[nDim_array:]
    if len(c_size) <= 1:
        c_size = tuple(c_size) + (1,) if c_size else (1,)
    c_length = int(np.prod(c_size))
    a = a.reshape(in_length, c_length)
    c = np.empty(c_length, dtype=object)
    for i in range(c_length):
        c[i] = a[:, i].reshape(in_size)
    c = c.reshape(c_size)
    return c
