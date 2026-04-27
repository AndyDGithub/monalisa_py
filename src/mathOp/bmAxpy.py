import numpy as np

def bmAxpy(a, x, y):
    if isinstance(a, list) and isinstance(x, list) and isinstance(y, list):
        N = np.shape(x[0].ravel(), 1)
        out = [None] * np.shape(x)[0]
        for i in range(N):
            out[i] = a[i]*x[i] + y[i]
    elif not isinstance(a, list) and isinstance(x, list) and isinstance(y, list):
        N = np.shape(x[0].ravel(), 1)
        out = [None] * np.shape(x)[0]
        if len(a) == 1:
            for i in range(N):
                out[i] = a*x[i] + y[i]
        else:
            for i in range(N):
                out[i] = a[i]*x[i] + y[i]
    elif not isinstance(a, list) and not isinstance(x, list) and not isinstance(y, list):
        if len(a) == 1:
            out = a*x + y
        else:
            out = a*x + y
    else:
        raise ValueError("In bmAxpy: case not implemented. ")

    return out
