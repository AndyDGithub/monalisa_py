from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
import numpy as np

def bmY_prod(y1, y2, d_n):
    if len(np.shape(y1)) > 2:
        raise ValueError("This function is for 2Dim arrays only.")
    if not (np.array_equal(np.shape(y1), np.shape(y2))):
        raise ValueError("Both arrays must have the same size.")

    d_n = bmY_ve_reshape(d_n, np.shape(y1))
    if y1.shape[0] > y1.shape[1]:
        p = np.sum(np.conj(y1) * (y2 * d_n), axis=1)
    else:
        p = np.sum(np.conj(y1) * (y2 * d_n), axis=2)

    return p
