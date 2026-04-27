import numpy as np
from src.arrayUtility import bmBlockReshape

def alpha(angle):
    return angle * (np.pi / 180)


def bmDoubleFA_solve(c, beta, ratio, precision):
    maxAngle = 0.9 * np.pi
    precision /= 2

    alpha = np.arange(0, maxAngle + precision, precision)
    f = (np.sin(ratio * alpha) / np.sin(alpha)) * (1 - np.cos(alpha) * beta) / (1 - np.cos(ratio * alpha) * beta)
    f[0] = f[1]

    f = np.maximum(f, -4)

    myIndex = np.argmin(np.abs(f - c))
    out = alpha[myIndex]

    return out
