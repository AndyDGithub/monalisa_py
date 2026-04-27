import numpy as np
from src.arrayUtility.bmZero import bmZero
from src.optim.bmBackGradient_nT import bmBackGradient_nT


def bmBackGradientT(g: np.ndarray, n_u: np.ndarray, dX_u: float) -> np.ndarray:
    imDim = np.shape(n_u)[1]
    nPt_u = np.prod(n_u)
    x = bmZero([nPt_u, 1], "complex64")

    for n in range(imDim):
        x = x + bmBackGradient_nT(g[:, n], n_u, dX_u, n)

    return x
