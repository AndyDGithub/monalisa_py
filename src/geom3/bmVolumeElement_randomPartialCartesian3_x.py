from __future__ import annotations
from third_part.matlab_compat.matlab_native import repmat, size

from src.geom2.bmVolumeElement_voronoi_box2 import bmVolumeElement_voronoi_box2

import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.geom2.bmVolumeElement_voronoi_box2 import bmVolumeElement_voronoi_
bmVolumeElement_voronoi_box2


def bmVolumeElement_randomPartialCartesian3_x(t, N_u, dK_u):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    N_u = np.atleast_2d(N_u).T
    dK_u = np.atleast_2d(dK_u).T

    Nx, Ny, Nz = N_u[0]
    dKx, dKy, dKz = dK_u[0]

    t = bmPointReshape(t)
    nPt = t.shape[1]
    nLine = nPt // Nx

    t = t.reshape((3, Nx, nLine))
    t1 = bmPointReshape(squeeze(t[2:4, 0, :]))
    ve = bmVolumeElement_voronoi_box2(t1, (Ny, Nz), (dKy, dKz))
    ve = np.tile(ve[:, None], (Nx, 1)).T
    ve *= dKx * np.ones_like(ve)

    return ve
