import numpy as np
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape from the correct path

def bmMinus(x, y):
    if isinstance(x, list) and isinstance(y, list):
        N = np.shape(np.asarray(x).ravel(), 1)
        out = [None] * len(x)
        for i in range(N):
            out[i] = bmBlockReshape(x[i] - y[i])
    elif not isinstance(x, list) and not isinstance(y, list):
        out = bmBlockReshape(x - y)
    elif not isinstance(x, list) and isinstance(y, list):
        N = np.shape(np.asarray(y).ravel(), 1)
        out = [None] * len(y)
        for i in range(N):
            out[i] = bmBlockReshape(x - y[i])
    else:
        raise ValueError("In bmMinus : case not implemented.")

    return out
