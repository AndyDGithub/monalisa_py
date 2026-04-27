import numpy as np


def bmRand(argSize, argType):
    argSize = tuple(np.array(argSize).ravel().astype(int))
    if argType == "real_double":
        return np.random.rand(*argSize)
    elif argType == "complex_double":
        return np.random.rand(*argSize) + 1j * np.random.rand(*argSize)
    elif argType == "real_single":
        return np.random.rand(*argSize).astype("float32")
    elif argType == "complex_single":
        return (np.random.rand(*argSize) + 1j * np.random.rand(*argSize)).astype("complex64")
    return np.random.rand(*argSize)
