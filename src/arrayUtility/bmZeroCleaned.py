import numpy as np


def bmZeroCleaned(argA):
    out = np.asarray(argA).ravel()
    return out[out != 0]
