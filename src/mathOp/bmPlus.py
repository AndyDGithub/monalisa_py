import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Importing 'arrayUtility' module to resolve ModuleNotFoundError

def bmPlus(x, y):
    if isinstance(x, list) and isinstance(y, list):
        N = len(x)
        out = [None] * N
        for i in range(N):
            out[i] = np.array(x[i]) + np.array(y[i])
        return out

    elif not isinstance(x, list) and not isinstance(y, list):
        return x + y

    else:
        raise ValueError("in bmPlus: case not implemented.")
