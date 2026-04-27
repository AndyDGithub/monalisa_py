import numpy as np


def bmSingle(a):
    if isinstance(a, list) or (isinstance(a, np.ndarray) and a.dtype == object):
        if isinstance(a, list):
            a = np.array(a, dtype=object)
        argSize = a.shape
        a_flat = a.ravel()
        out = np.empty_like(a_flat)
        for i in range(len(a_flat)):
            out[i] = np.asarray(a_flat[i]).astype("float32")
        return out.reshape(argSize)
    return np.asarray(a).astype("float32")
