import numpy as np
from scipy.special import iv

def bmKaiser(x, alpha, tau):
    """Compute the Kaiser window function.

    Parameters
    ----------
    x : array_like
        Input array of positions.
    alpha : float
        Shape parameter.
    tau : float
        Scaling parameter.

    Returns
    -------
    ndarray
        Kaiser window values corresponding to ``x``.
    """
    x_arr = np.asarray(x)
    I0alpha = iv(0, alpha)
    y = np.maximum(1 - (x_arr / tau) ** 2, 0)
    y = alpha * np.sqrt(y)
    y = iv(0, y) / I0alpha
    return y

# Import statement for the missing function from src.geom123 module
from src.geom123 import bmTraj
