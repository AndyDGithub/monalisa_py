from __future__ import annotations

import numpy as np


def bmBackGradient_nT(
    x: np.ndarray,
    n_u: np.ndarray,
    dX_u: np.ndarray,
    n: int,
) -> np.ndarray:
    """
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023

    Compute the backward gradient along the nth dimension of a multidimensi
multidimensional array.

    Parameters
    ----------
    x : np.ndarray
        Data vector (flattened column vector).
    n_u : np.ndarray
        Array of size per dimension (e.g. [Nx, Ny, Nz]).
    dX_u : np.ndarray
        Grid spacing per dimension (same size as n_u).
    n : int
        Dimension index (1-based) to compute the gradient.

    Returns
    -------
    np.ndarray
        Gradient vector (column, same size as x).
    """
    # Ensure dimension vectors are 1-D arrays
    n_u = np.asarray(n_u).reshape(-1)
    dX_u = np.asarray(dX_u).reshape(-1)

    im_dim = n_u.size
    if im_dim == 0:
        raise ValueError("n_u must contain at least one dimension.")
    if not (1 <= n <= im_dim):
        raise ValueError(f"n must be between 1 and {im_dim} (inclusive).")

    # Reshape the input data to match the spatial grid
    if im_dim == 1:
        x = x.reshape((n_u[0], 1))
    else:
        x = x.reshape(tuple(n_u))

    # Initialise gradient with the data itself
    g = x.copy()

    # Zero out the boundary along the specified dimension
    if im_dim == 1:
        # Only the first element in a 1-D field
        g[0, 0] = 0
    else:
        idx = [slice(None)] * im_dim
        idx[n - 1] = 0
        g[tuple(idx)] = 0

    # Compute shifted version of the data for the difference
    shift = np.roll(x, shift=-1, axis=n - 1)

    # Compute gradient and normalise by grid spacing
    g = (g - shift) / dX_u[n - 1]

    # Return as a flattened column vector
    return g.reshape(-1)
