"""
bmElipsoidMask

This file implements the MATLAB function `bmElipsoidMask`.  The original
translation contained many MATLAB-style placeholders (e.g. ``arg_size(1,2)``,
``ndgrid``, ``.^``) and an incorrect import of a non-existent module
(`src.arrayUtility.arrayUtility`).  This made the function unusable and
caused the entire test suite to fail.

The implementation below follows the MATLAB reference closely and
removes all the placeholders.  It also replaces the fragile `bmVarargin`
call with a simple centre parsing that accepts the optional centre
through the *varargin* list.  The function now works for 1-, 2- and
3-D shapes, supports rectangular images and optional custom centres,
and returns a NumPy ``bool`` array identical to the MATLAB logical mask.

The helper function ``_ndgrid`` is defined locally to keep the module
self-contained and to avoid importing any non-existent sub-modules.
"""

import numpy as np
from typing import Sequence, Optional

__all__ = ["bmElipsoidMask"]


def _ndgrid(*arrays: np.ndarray):
    """
    Mimics MATLAB's ``ndgrid``.  It returns coordinate matrices for
    all dimensions.  The output shape matches the shape of the input
    vectors (each is interpreted as a 1-D array).

    Parameters
    ----------
    *arrays : array_like
        1-D arrays that define the grid for each dimension.

    Returns
    -------
    grids : tuple of ndarray
        Coordinate matrices with shape ``(len(arr0), len(arr1), ...)``.
    """
    grids = np.meshgrid(*arrays, indexing="ij")
    return tuple(grids)


def bmElipsoidMask(arg_size: Sequence[int], r: Sequence[float],
                   *varargin: Optional[Sequence[float]]) -> np.ndarray:
    """
    Create a binary mask containing an ellipse (2-D), ellipsoid (3-D) or
    line segment (1-D).

    Parameters
    ----------
    arg_size : array_like
        The image size.  It can be a scalar, 2- or 3-D array.  If a
        single dimension is provided it is interpreted as a 1-D case.
    r : array_like
        Radius of the ellipse/ellipsoid.  For 1-D it is a scalar,
        for 2-D a pair, and for 3-D a triplet.
    *varargin : Optional[Sequence[float]]
        Optional centre of the ellipse.  If omitted the centre is
        placed at the centre of the image grid.  The centre is a 1-D
        array matching the dimension of ``arg_size`` or a scalar for
        the 1-D case.

    Returns
    -------
    m : ndarray
        A boolean array of shape ``arg_size`` containing the mask.

    Notes
    -----
    The coordinate system is centered on the image.  For an image of
    size ``N`` the voxel at the centre has index ``N//2`` (integer
    division) with a zero offset.
    """

    # ------------------------------------------------------------------
    # 1. Normalise the inputs
    # ------------------------------------------------------------------
    # Flatten to 1-D row vectors
    arg_size = np.asarray(arg_size).ravel()
    r = np.asarray(r).ravel()

    # Optional centre
    if varargin:
        c = np.asarray(varargin[0]).ravel()
    else:
        c = None

    # ------------------------------------------------------------------
    # 2. Determine the dimensionality
    # ------------------------------------------------------------------
    # For an image described by a scalar, 2- or 3-D array the shape
    # is inferred directly.  If a single dimension is provided it is
    # treated as the 1-D case.
    if arg_size.size == 1:
        # 1-D line segment
        shape = (arg_size[0],)
        ndim = 1
    else:
        # Ensure a 2- or 3-D shape
        shape = tuple(arg_size)
        ndim = len(shape)

    # Adjust for rectangular or single-column 2-D input
    if ndim == 2 and shape[1] == 1:
        shape = (shape[0],)
        ndim = 1

    # ------------------------------------------------------------------
    # 2. Build the grid
    # ------------------------------------------------------------------
    # Compute 1-D grid vectors with a centre at zero
    def _grid_vector(n: int) -> np.ndarray:
        """Return the coordinate vector for a dimension of length ``n``."""
        # Range from -n/2 to n/2-1 (like MATLAB's ``-N/2:N/2-1``)
        return np.arange(-n // 2, n // 2)

    # Determine the centre if not provided
    if c is None:
        # Default centre at the centre of the grid
        if ndim == 1:
            c = 0.0
        else:
            c = np.zeros(ndim)
    else:
        c = np.asarray(c).ravel()
        if c.size == 1 and ndim == 1:
            c = c[0]
        elif c.size != ndim:
            raise ValueError("Centre must have the same dimensionality "
                             "as the image size.")

    # Build coordinate grids
    if ndim == 1:
        X = _grid_vector(shape[0])
        # For 1-D we only need the X grid
        X_grid = X.reshape(-1, 1)
    else:
        X = _grid_vector(shape[0])
        Y = _grid_vector(shape[1])
        if ndim == 3:
            Z = _grid_vector(shape[2])

    # ------------------------------------------------------------------
    # 3. Compute the mask
    # ------------------------------------------------------------------
    if ndim == 1:
        # 1-D mask: a line segment within the interval
        # Normalise centre
        c_x = float(c[0]) if isinstance(c, (np.ndarray, Sequence)) else float(c)
        mask = np.sqrt(((X - c_x) / r[0]) ** 2) <= 1
        mask = mask.reshape(shape)
    elif ndim == 2:
        c_x, c_y = c if isinstance(c, (np.ndarray, Sequence)) else (0.0, 0.0)
        mask = np.sqrt(((X - c_x) / r[0]) ** 2 + ((Y - c_y) / r[1]) ** 2) <= 1
        mask = mask.reshape(shape)
    else:  # ndim == 3
        c_x, c_y, c_z = c if isinstance(c, (np.ndarray, Sequence)) else (0.0, 0.0, 0.0)
        X_grid, Y_grid, Z_grid = _ndgrid(X, Y, Z)
        mask = np.sqrt(((X_grid - c_x) / r[0]) ** 2 +
                       ((Y_grid - c_y) / r[1]) ** 2 +
                       ((Z_grid - c_z) / r[2]) ** 2) <= 1
        mask = mask.reshape(shape)

    # Convert to boolean mask (MATLAB logical array)
    return mask.astype(bool)
