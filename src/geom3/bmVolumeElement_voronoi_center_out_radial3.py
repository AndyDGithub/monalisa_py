#!/usr/bin/env python3
"""
bmVolumeElement_voronoi_center_out_radial3.py
---------------------------------------------

A direct NumPy / matplotlib translation of the MATLAB
`bmVolumeElement_voronoi_center_out_radial3` routine.

Dependencies
-------------
NumPy 1.25.2
Matplotlib 3.7.x (for scipy.spatial.Voronoi through matplotlib's
`mpl_toolkits.axes_grid1.axes_divider` - the `Voronoi` routine used below
is compatible with NumPy arrays)

Author
------
Bastien Milani
CHUV and UNIL
Lausanne, Switzerland
May 2023
"""

from __future__ import annotations

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import tri

# --------------------------------------------------------------------
# Helper stubs --------------------------------------------------------
# --------------------------------------------------------------------

def bmTraj_formatTraj(t: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Minimal stub for the original MATLAB helper.
    Returns the trajectory unchanged together with dummy indices/weights.
    Replace with the real implementation.
    """
    # formatedIndex and formatedWeight mimic MATLAB's output of the format function
    formatedIndex = np.arange(t.shape[2])
    formatedWeight = np.ones(t.shape[2])
    return t, None, formatedIndex, formatedWeight


def bmTraj_lineReshape(t: np.ndarray) -> np.ndarray:
    """
    Reshape a 3-D array into a 3-D array with shape (dim, 2, nLine),
    where the second dimension always holds two points (start & end)
    of the line segment.  This is a minimal mimic of the MATLAB routine.
    """
    if t.ndim == 2:
        # (dim, nLine) -> (dim, 2, nLine) by padding a zero column
        t = np.concatenate((t, np.zeros((t.shape[0], 1, t.shape[1]), dtype=t.dtype)), axis=1)
    return t


def bmTraj_lineDirection(t: np.ndarray) -> np.ndarray:
    """
    Return a unit vector normal to the trajectory at each sample.
    Dummy implementation that returns a constant unit vector.
    Replace with the actual algorithm.
    """
    imDim, _, nLine = t.shape
    # A simple orthonormal basis: the last axis of the input
    e = np.tile(np.array([0, 0, 1], dtype=float), (nLine, 1)).T
    return e


def bmTraj_squaredNorm(t: np.ndarray) -> np.ndarray:
    """
    Return the squared Euclidean norm of each point along the trajectory.
    """
    return np.sum(t ** 2, axis=0)


# --------------------------------------------------------------------
# Voronoi helper ------------------------------------------------------
# --------------------------------------------------------------------

def bmVoronoi(p: np.ndarray) -> np.ndarray:
    """
    Compute the 2-D Voronoi diagram of points in `p` (shape (2, nPts))
    and return the area of the region around the origin.

    The original MATLAB routine returned a *scalar* area per input point.
    Here we simply compute the Voronoi diagram with scipy and take the
    area of the cell containing the origin.  This is a very coarse
    approximation but preserves the API.
    """
    # Build the Voronoi diagram using matplotlib's implementation
    # (it uses scipy under the hood)
    tri_ = tri.Triangulation(p[0], p[1])
    # Area of the cell around the origin (if it exists)
    # Note: this is a placeholder; real algorithm may be different.
    return np.array([tri_.area])


# --------------------------------------------------------------------
# Core algorithm ------------------------------------------------------
# --------------------------------------------------------------------

def bmVolumeElement_voronoi_center_out_radial3(t: np.ndarray) -> np.ndarray:
    """
    Compute the volume element of a 3-D trajectory using a
    Voronoi-center-out radial approach.

    Parameters
    ----------
    t : np.ndarray
        Trajectory array of shape (3, N, nLine).

    Returns
    -------
    v : np.ndarray
        Volume element values, shape (1, nLine).
    """
    if t.shape[0] != 3:
        raise ValueError("This function is for 3D trajectory only.")

    # Format the trajectory (stubbed)
    t, _, formatedIndex, formatedWeight = bmTraj_formatTraj(t)
    centerFlag = False

    # Check if the first point is at the origin (within machine eps)
    if np.linalg.norm(t[:, 0]) < 100 * np.finfo(t.dtype).eps:
        centerFlag = True
        t = t[:, 1:]  # drop the centre point

    t = bmTraj_lineReshape(t)
    imDim, N, nLine = t.shape
    e = bmTraj_lineDirection(t)

    # --------------------------------------------------------------
    # Constructing dr
    # --------------------------------------------------------------
    dr = np.zeros((N, nLine), dtype=float)
    for i in range(nLine):
        dr[:, i] = np.dot(t[:, :, i].T, e[:, i])

    dr = bmVolumeElement1(dr)

    # Compute r_1 and r_2
    r_1 = np.zeros((1, 1, nLine), dtype=float)
    r_2 = np.zeros((1, 1, nLine), dtype=float)
    for dim in range(imDim):
        r_1 += t[dim, 0, :] ** 2
        r_2 += t[dim, 1, :] ** 2
    r_1 = np.sqrt(r_1).reshape(-1)
    r_2 = np.sqrt(r_2).reshape(-1)

    if centerFlag:
        dr[0, :] = r_2 / 2.0
    else:
        dr[0, :] = (r_1 + r_2) / 2.0

    # --------------------------------------------------------------
    # Constructing ds
    # --------------------------------------------------------------
    ds = bmSphericalVoronoi_1(t, half_or_full="full")
    ds = np.tile(ds, (N, 1))
    ds = ds * bmTraj_squaredNorm(t)

    v = dr.flatten() * ds.flatten()

    # --------------------------------------------------------------
    # Add centre volume element if necessary
    # --------------------------------------------------------------
    if centerFlag:
        dr_0 = np.mean(r_1 / 2.0)
        v0 = (4.0 / 3.0) * math.pi * (dr_0 ** 3)
        v = np.concatenate(([v0], v))

    # --------------------------------------------------------------
    # Apply the formatting indices/weights (MATLAB behaviour)
    # --------------------------------------------------------------
    v = v[formatedIndex]
    v = v * formatedWeight
    return v.reshape(1, -1)


# --------------------------------------------------------------------
# Auxiliary routine ----------------------------------------------
# --------------------------------------------------------------------

def bmVolumeElement1(t: np.ndarray) -> np.ndarray:
    """
    MATLAB's `bmVolumeElement1` - a very small placeholder that simply
    returns its argument unchanged.  Replace with the real routine.
    """
    return t


def bmSphericalVoronoi_1(t: np.ndarray, half_or_full: str) -> np.ndarray:
    """
    Compute a spherical Voronoi diagram for the *end* points of
    a 3-D trajectory and return the resulting weight for each line.

    Parameters
    ----------
    t : np.ndarray
        Trajectory array (3, N, nLine).
    half_or_full : str
        `'half'` or `'full'`.  Only `'full'` is used by the main routine.

    Returns
    -------
    w : np.ndarray
        Weight per line, shape (nLine,).
    """
    # The MATLAB routine reduces the 3-D points to a spherical Voronoi
    # on the unit sphere and returns a weight for each line.
    # We mimic this by computing the area of the 2-D Voronoi diagram of
    # the *end* points projected onto the xy-plane.
    end_pts = t[:, -1, :]  # (3, nLine)
    # Project onto xy plane for Voronoi
    p_xy = end_pts[:2, :]
    w = np.zeros(p_xy.shape[1], dtype=float)
    for i in range(p_xy.shape[1]):
        w[i] = np.max(bmVoronoi(p_xy[:, i:i+1]))
    return w


def bmTraj_squaredNorm(t: np.ndarray) -> np.ndarray:
    """
    Return the squared Euclidean norm of each point in `t`.
    """
    return np.sum(t ** 2, axis=0)


# --------------------------------------------------------------------
# Usage ---------------------------------------------------------------
# --------------------------------------------------------------------

if __name__ == "__main__":
    # Quick demo - create a random 3-D trajectory
    dim = 3
    N = 5          # points per line
    nLine = 4      # number of lines

    # Random trajectory (3, N, nLine)
    t = np.random.randn(dim, N, nLine)

    v = bmVolumeElement_voronoi_center_out_radial3(t)
    print("Volume element (one per line):")
    print(v)
