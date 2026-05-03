import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmSinc(x):
    """Compute the sinc function.
    
    The sinc function is defined as sin(x)/x. This implementation handles
    edge cases where the input is zero or very close to zero, and also
    replaces NaN or Inf values with 1.

    Parameters
    ----------
    x : array_like
        Points at which to evaluate the sinc function.

    Returns
    -------
    f : ndarray
        The sinc function evaluated at `x`.
    """
    myEps = 1e-4
    f = np.sin(x) / x
    mask = np.isnan(f) | np.isinf(f) | (x == 0) | (np.abs(x) < myEps)
    f[mask] = 1
    return f
