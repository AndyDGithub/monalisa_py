import numpy as np


def bmOne(argSize, argType):
    if argType == "real_double":
        return np.ones(argSize, dtype="float64")
    elif argType == "complex_double":
        return np.ones(argSize, dtype="complex128")
    elif argType == "real_single":
        return np.ones(argSize, dtype="float32")
    elif argType == "complex_single":
        return np.ones(argSize, dtype="complex64")
    return np.ones(argSize)
