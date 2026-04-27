import numpy as np
from src.varargin.bmVarargin import bmVarargin


def bmZero(argSize, argType, *varargin):
    frame_size = bmVarargin(varargin)

    if frame_size is not None and frame_size != [] and len(np.asarray(frame_size).ravel()) > 0:
        frame_size = tuple(np.array(frame_size).ravel().astype(int))
        z = np.empty(frame_size, dtype=object)
        for i in range(z.size):
            z.ravel()[i] = bmZero(argSize, argType)
        return z

    if argType == "real_double":
        return np.zeros(argSize, dtype="float64")
    elif argType == "complex_double":
        return np.zeros(argSize, dtype="complex128")
    elif argType == "real_single":
        return np.zeros(argSize, dtype="float32")
    elif argType == "complex_single":
        return np.zeros(argSize, dtype="complex64")
    return np.zeros(argSize)
