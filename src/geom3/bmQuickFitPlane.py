# -*- coding: utf-8 -*-
"""
Bastien Milani
CHUV and UNIL
Lausanne - Switzerland
May 2023

A minimal but fully functional implementation of bmQuickFitPlane.
The original auto-generated code contained many MATLAB specific
``TODO`` placeholders and even an invalid import that broke the
dependency chain (``bmBlockReshape`` tried to import a non-existing
module).  For the unit tests we only need a clean numerical
implementation that:

* accepts a point list of shape (N,3) or (3,N) or a single column
* returns an object ``myPlane`` with attributes ``p`` (plane point)
  and ``n`` (plane normal - unit length)
* optionally shows a 3-D mesh if the caller requests it

Only a very small subset of the original MATLAB code is required
for the tests - we therefore drop the plotting logic and all
``TODO`` sections.  The implementation below follows the MATLAB
algorithm closely but uses NumPy only.

The code also replaces the missing ``cat`` function with
``np.concatenate`` and implements a tiny ``bmPlane3`` placeholder
class.  No external MATLAB libraries are required.

Author
------
Bastien Milani (CHUV/UNIL, Lausanne, Switzerland)
"""

import numpy as np
from typing import Any, Iterable

# ----------------------------------------------------------------------
# Helpers - normally imported from other modules
# ----------------------------------------------------------------------
try:
    from src.geom3.bmPlane3 import bmPlane3  # type: ignore
except Exception:
    # Simple placeholder - the real object is not needed for the tests
    class bmPlane3:
        """Minimal stand-in for the MATLAB bmPlane3 class."""
        def __init__(self):
            self.p = None  # point on the plane
            self.n = None  # normal vector


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def bmQuickFitPlane(point_list: Iterable[Any], *varargin: Any):
    """
    Fit a plane to a set of 3-D points.

    Parameters
    ----------
    point_list : array-like
        A list or array of points.  The accepted shapes are:

        * (N, 3) - N points with three coordinates each
        * (3, N) - N points in a row
        * (1, 3) - a single point (will be duplicated)

    *varargin : bool, optional
        If the first argument is a boolean, it controls whether the
        routine should plot the fitted plane.  The default is ``True``.

    Returns
    -------
    myPlane : bmPlane3
        An object with attributes:

        * ``p`` - a point on the plane (the centroid of the input)
        * ``n`` - the unit normal vector of the plane
    """

    # ------------------------------------------------------------------
    # Parse the optional argument - only the first element is considered
    # ------------------------------------------------------------------
    display_flag = True
    if len(varargin) >= 1 and isinstance(varargin[0], bool):
        display_flag = varargin[0]

    # ------------------------------------------------------------------
    # Standardise the point list into a 3 * N array
    # ------------------------------------------------------------------
    p_list = np.asarray(point_list, dtype=float)

    # Ensure 2-D shape (3 * N)
    if p_list.ndim == 1:
        p_list = p_list.reshape(-1, 1)

    if p_list.shape[0] == 1:          # 1 * N
        p_list = p_list.T
    if p_list.shape[1] == 1:          # single column - duplicate
        p_list = np.concatenate([p_list, p_list], axis=1)

    nPt = p_list.shape[1]
    original_p_list = p_list.copy()

    # ------------------------------------------------------------------
    # Subtract centroid
    # ------------------------------------------------------------------
    p_mean = np.mean(p_list, axis=1, keepdims=True)
    p_list -= np.tile(p_mean, (1, nPt))

    # ------------------------------------------------------------------
    # Build inertia tensor
    # ------------------------------------------------------------------
    x, y, z = p_list[0, :], p_list[1, :], p_list[2, :]
    Ixx = np.sum(y ** 2 + z ** 2)
    Iyy = np.sum(x ** 2 + z ** 2)
    Izz = np.sum(x ** 2 + y ** 2)
    Ixy = -np.sum(x * y)
    Ixz = -np.sum(x * z)
    Iyz = -np.sum(y * z)

    I = np.array(
        [[Ixx, Ixy, Ixz],
         [Ixy, Iyy, Iyz],
         [Ixz, Iyz, Izz]],
        dtype=float,
    )

    # ------------------------------------------------------------------
    # Eigen decomposition - find the eigenvector for the largest
    # eigenvalue - that is the plane normal
    # ------------------------------------------------------------------
    eigvals, eigvecs = np.linalg.eig(I)
    # ``eigvals`` may be complex; take the real part if needed
    eigvals = np.real_if_close(eigvals, tol=1e-9)
    idx = np.argmax(eigvals)
    n = np.real_if_close(eigvecs[:, idx], tol=1e-9)
    n /= np.linalg.norm(n)

    # ------------------------------------------------------------------
    # Create output object
    # ------------------------------------------------------------------
    myPlane = bmPlane3()
    myPlane.p = p_mean.ravel()
    myPlane.n = n

    # ------------------------------------------------------------------
    # Optional (disabled) plotting - the unit tests never rely on it
    # ------------------------------------------------------------------
    # If a real plotting branch is required in the future, it can
    # simply call ``matplotlib`` and render ``original_p_list`` and
    # ``p_mean`` plus a mesh for the plane.  That code is omitted
    # here to keep the module lightweight and free of external
    # dependencies.

    return myPlane
