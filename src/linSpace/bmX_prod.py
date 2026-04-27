import numpy as np

def bmX_prod(x1, x2, d_u):
    if x1.ndim > 2:
        raise ValueError("This function is for 2Dim arrays only.")
    if not np.array_equal(x1.shape, x2.shape):
        raise ValueError("Both arrays must have the same size.")

    dV = np.prod(d_u.ravel())
    if x1.shape[0] > x1.shape[1]:
        p = np.sum(np.conj(x1) * (x2 * dV), axis=1)
    else:
        p = np.sum(np.conj(x1) * (x2 * dV), axis=2)

    return p
