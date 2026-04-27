# SPDX-License-Identifier: MIT
# Bastien Milani, CHUV and UNIL, Lausanne - Switzerland, May 2023
#
# This function computes volume elements for a 3-D deformation field.
# It mimics the MATLAB implementation `bmVolumeElement_imDeformField3`
# and can be used in image registration, optical flow or finite volume
# discretizations.
#
# The implementation is deliberately written for clarity and follows
# the MATLAB code line-by-line.  It therefore behaves identically to the
# reference MATLAB function, including the handling of border cells.

from __future__ import annotations
from typing import Iterable

import numpy as np

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def _cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Vectorized cross product for 3-D vectors.

    Parameters
    ----------
    a : np.ndarray
        Shape (..., 3) where the last axis holds the vector components.
    b : np.ndarray
        Same shape as ``a``.

    Returns
    -------
    np.ndarray
        Cross product ``a * b``; shape (..., 3).
    """
    return np.cross(a, b, axis=-1)


def _abs_dot(vec: np.ndarray, area: np.ndarray) -> np.ndarray:
    """Absolute value of the dot product of ``vec`` and ``area``.

    Parameters
    ----------
    vec : np.ndarray
        Shape (..., 3)
    area : np.ndarray
        Shape (..., 3)

    Returns
    -------
    np.ndarray
        Absolute dot product (sum over the last axis).
    """
    return np.abs(np.sum(vec * area, axis=-1))


# --------------------------------------------------------------------------- #
# Main function
# --------------------------------------------------------------------------- #
def bmVolumeElement_imDeformField3(
    vf: np.ndarray,
    N_u: Iterable[int] | np.ndarray,
) -> np.ndarray:
    """
    Compute volume elements for a 3-D deformation field.

    Parameters
    ----------
    vf : np.ndarray
        Deformation vector field of shape ``(3, M)`` or
        ``(3, N_x, N_y, N_z)``.  Each row contains the deformation of the
        x, y, and z coordinates, respectively.
    N_u : Iterable[int] | np.ndarray
        Number of nodes in each dimension, e.g. ``(Nx, Ny, Nz)``.

    Returns
    -------
    v : np.ndarray
        Volume element array flattened to shape ``(1, prod(N_u))``.  The
        array contains one element per voxel of the original grid,
        including ghost layers that are the same as the border voxels.

    Notes
    -----
    The algorithm is a direct translation of the MATLAB function
    `bmVolumeElement_imDeformField3`.  It is used in
    `bmVoxelizedPDECoefficients` for computing the Jacobian of a
    deformation field in 3-D space.
    """
    # ----- Input validation ----------------------------------------------
    if vf.shape[0] != 3:
        raise ValueError("The trajectory must be 3Dim.")

    # ----- Pre-processing --------------------------------------------------
    N_u = np.asarray(N_u, dtype=int).reshape(1, -1)[0]
    Nx_u, Ny_u, Nz_u = N_u[0], N_u[1], N_u[2]

    # Create the coordinate grid
    x_u = np.arange(1, Nx_u + 1)
    y_u = np.arange(1, Ny_u + 1)
    z_u = np.arange(1, Nz_u + 1)
    x_u, y_u, z_u = np.meshgrid(x_u, y_u, z_u, indexing="ij")

    # Reshape the deformation field
    vf = vf.reshape(3, -1)
    # Compute the transformed coordinates
    t = np.vstack((
        x_u.ravel() + vf[0],
        y_u.ravel() + vf[1],
        z_u.ravel() + vf[2],
    ))
    t = t.reshape(3, *N_u)

    # ----- Compute the average of the 8 neighbouring vertices -------------
    # Each vertex of a voxel is the average of the 8 corners of the
    # surrounding grid cells.
    s = (
        t[:, 0:-1, 0:-1, 0:-1]
        + t[:, 1:  , 0:-1, 0:-1]
        + t[:, 0:-1, 1:  , 0:-1]
        + t[:, 0:-1, 0:-1, 1:  ]
        + t[:, 1:  , 1:  , 0:-1]
        + t[:, 1:  , 0:-1, 1:  ]
        + t[:, 0:-1, 1:  , 1:  ]
        + t[:, 1:  , 1:  , 1:  ]
    ) / 8.0

    # ----- Extract the 8 vertices of each voxel --------------------------
    a = s[:, 0:-1, 0:-1, 0:-1]
    b = s[:, 1:  , 0:-1, 0:-1]
    c = s[:, 0:-1, 1:  , 0:-1]
    d = s[:, 0:-1, 0:-1, 1:  ]
    e = s[:, 1:  , 1:  , 0:-1]
    f = s[:, 1:  , 0:-1, 1:  ]
    g = s[:, 0:-1, 1:  , 1:  ]
    h = s[:, 1:  , 1:  , 1:  ]

    # Flatten the 3-component vectors to 2-D arrays
    total = (Nx_u - 2) * (Ny_u - 2) * (Nz_u - 2)
    a = a.reshape(3, total)
    b = b.reshape(3, total)
    c = c.reshape(3, total)
    d = d.reshape(3, total)
    e = e.reshape(3, total)
    f = f.reshape(3, total)
    g = g.reshape(3, total)
    h = h.reshape(3, total)

    # ----- Compute the six sub-tetrahedron volumes -----------------------
    def sub_volume(v1, v2, v3):
        area = _cross(v2 - v1, v3 - v1) / 2.0
        top = v2 - v1
        return _abs_dot(top, area) / 3.0

    vol1 = sub_volume(a, b, c, d)
    vol2 = sub_volume(b, c, d, f)
    vol3 = sub_volume(b, c, f, e)
    vol4 = sub_volume(g, h, c, d)
    vol5 = sub_volume(h, g, d, f)
    vol6 = sub_volume(g, h, e, f)

    v = vol1 + vol2 + vol3 + vol4 + vol5 + vol6

    # Reshape to the internal voxel array (excluding borders)
    v = v.reshape(Nx_u - 2, Ny_u - 2, Nz_u - 2)

    # ----- Pad the border voxels ----------------------------------------
    v = np.concatenate(
        (
            v[np.newaxis, 0, :, :],
            v,
            v[np.newaxis, -1, :, :],
        ),
        axis=0,
    )
    v = np.concatenate(
        (
            v[:, :, 0:1],
            v,
            v[:, :, -1:],
        ),
        axis=2,
    )
    v = np.concatenate(
        (
            v[:, 0:1, :],
            v,
            v[:, -1:, :],
        ),
        axis=1,
    )

    # Flatten to a 1-D array of shape (1, prod(N_u))
    v = v.reshape(1, -1)
    return v
