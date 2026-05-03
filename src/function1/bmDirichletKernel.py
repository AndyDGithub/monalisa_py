# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np


def bmDirichletKernel(x, N):
    """
    Compute the Dirichlet kernel for the given points ``x`` and parameter `
``N``.

    MATLAB implementation:

    f = sin((N+1/2)*x) ./ sin(x/2);
    f(isinf(f) | ~isnumeric(f) | isnan(f) | (abs(sin(x/2)) < 1e-4)) = 2*N+1
2*N+1;

    Parameters
    ----------
    x : array_like
        Points at which the kernel is evaluated.
    N : int or array_like
        Parameter of the Dirichlet kernel.

    Returns
    -------
    ndarray
        Kernel values evaluated at ``x``.
    """
    myEps = 1e-4
    x_arr = np.asarray(x)
    denom = np.sin(x_arr / 2.0)
    f = np.sin((N + 0.5) * x_arr) / denom
    mask = np.isinf(f) | np.isnan(f) | (np.abs(denom) < myEps)
    f = np.where(mask, 2 * N + 1, f)
    return f
