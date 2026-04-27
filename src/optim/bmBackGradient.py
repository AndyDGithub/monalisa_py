from src.arrayUtility.bmZero import bmZero
import numpy as np
from src.optim.bmBackGradient_n import bmBackGradient_n


def bmBackGradient(x, n_u, dX_u):
    imDim = np.shape(n_u)[1]  # Adjusted to match NumPy shape function
    nPt_u = np.prod(n_u)
    g = bmZero([nPt_u, imDim], "complex64")

    for n in range(imDim):  # Replaced TODO with a Python loop
        g[:, n] = bmBackGradient_n(x, n_u, dX_u, n)

    return g
