import numpy as np

def bmMult(x, y):
    if isinstance(x, list) and isinstance(y, list):
        N = len(x[0])
        out = [[] for _ in x]
        for i in range(N):
            out[i] = [a * b for a, b in zip(x[i], y[i])]
    elif not isinstance(x, list) and isinstance(y, list):
        N = len(y[0])
        out = [[] for _ in y]
        for i in range(N):
            out[i] = x * y[i]
    elif not isinstance(x, list) and not isinstance(y, list):
        out = x * y
    else:
        raise ValueError("Invalid input types. Both inputs must be either lists or scalars.")

    return out
