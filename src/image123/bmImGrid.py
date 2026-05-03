# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from __future__ import annotations

import numpy as np


def bmImGrid(n_u, X=None, Y=None, Z=None):
    """
    Generate image grid based on input dimensions.

    Parameters
    ----------
    n_u : array_like
        Vector of dimensions. For 2-D, length 2; for 3-D, length 3.
    X, Y, Z : array_like, optional
        Pre-defined grid coordinates. If any are ``None``, the function gen
generates
        them using ``ndgrid`` semantics.

    Returns
    -------
    X, Y, Z : ndarray or np.ndarray
        Coordinate grids. ``Z`` is an empty array for 2-D inputs, matching
        MATLAB behaviour where the third output is empty.
    """
    n_u = np.asarray(n_u).reshape(-1)
    im_dim = len(n_u)

    if im_dim == 2:
        if X is None or Y is None:
            x = np.arange(1, n_u[0] + 1)
            y = np.arange(1, n_u[1] + 1)
            X, Y = np.meshgrid(x, y, indexing="ij")
        Z = np.array([])
    elif im_dim == 3:
        if X is None or Y is None or Z is None:
            x = np.arange(1, n_u[0] + 1)
            y = np.arange(1, n_u[1] + 1)
            z = np.arange(1, n_u[2] + 1)
            X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    else:
        raise ValueError("n_u must be a vector of length 2 or 3")

    return X, Y, Z

# MATLAB reference:
# % Bastien Milani
# % CHUV and UNIL
# % Lausanne - Switzerland
# % May 2023
#
# function [X, Y, Z] = bmImGrid(n_u, X, Y, Z)
#
# n_u = n_u(:)';
# imDim = size(n_u(:), 1);
#
# if imDim == 2
#     if isempty(X) || isempty(Y)
#         [X, Y] = ndgrid(1:n_u(1, 1), 1:n_u(1, 2));
#     end
# elseif imDim == 3
#     if isempty(X) || isempty(Y) || isempty(Z)
#         [X, Y, Z] = ndgrid(1:n_u(1, 1), 1:n_u(1, 2), 1:n_u(1, 3));
#     end
# end
#
# end
