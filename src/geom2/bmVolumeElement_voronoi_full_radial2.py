from __future__ import annotations
import numpy as np


def bmVolumeElement_voronoi_full_radial2(t):
    """Compute Voronoi volume elements for a 2D full radial trajectory.

    Parameters:
    t (array): 2D trajectory of shape (2, N_total) where N_total = N * nLine.

    Returns:
    v (array): Volume elements of length N_total, one per trajectory point.
    """
    from src.traj123.bmTraj_lineReshape import bmTraj_lineReshape
    from src.geom1.bmVolumeElement1 import bmVolumeElement1
    from src.traj123.bmTraj_lineDirection import bmTraj_lineDirection
    from src.geom123.bmVoronoi import bmVoronoi
    from src.traj123.bmTraj_norm import bmTraj_norm

    t = np.asarray(t)
    if t.shape[0] != 2:
        raise ValueError("The trajectory must be 2D")

    # Reshape flat trajectory to (2, N, nLine)
    t_line = bmTraj_lineReshape(t)  # (2, N, nLine)
    imDim  = t_line.shape[0]
    N      = t_line.shape[1]
    nLine  = t_line.shape[2]

    # Direction unit vectors for each line: shape (2, nLine)
    e = bmTraj_lineDirection(t_line)

    # Radial volume element: projection of each point onto line direction
    dr = np.zeros((N, nLine))
    for i in range(nLine):
        dr[:, i] = t_line[:, :, i].T @ e[:, i]
    dr = bmVolumeElement1(dr)  # (N, nLine)

    # Angular Voronoi weights using doubled direction set (e and -e)
    ee = np.concatenate([e, -e], axis=1)           # (2, 2*nLine)
    myAngle   = np.arctan2(ee[1, :], ee[0, :])     # (2*nLine,)
    myPerm    = np.argsort(myAngle)
    myInvPerm = np.argsort(myPerm)

    myAngle_sorted   = myAngle[myPerm]
    myAngleVoronoi   = bmVoronoi(myAngle_sorted)   # (2*nLine,) Voronoi widths in sorted order
    myAngleVoronoi   = myAngleVoronoi[myInvPerm]   # restore original order
    myAngleVoronoi   = myAngleVoronoi.reshape(2, nLine)  # (2, nLine): original + mirrored
    ds_angle         = myAngleVoronoi[0, :]        # (nLine,) angular widths for original directions

    # Angular area element: norm(t) * sin(angular_voronoi_width)
    norm_t = bmTraj_norm(t_line)  # (N, nLine) or flattened
    if norm_t.shape != (N, nLine):
        norm_t = norm_t.reshape(N, nLine)

    ds = norm_t * np.sin(ds_angle.reshape(1, nLine))  # (N, nLine)

    # Volume element = radial * angular
    v = dr.ravel() * ds.ravel()

    # Correct the center volume element (k=0 region)
    half  = N // 2
    dr_0  = float(np.mean(dr[half, :]))
    v0    = np.pi * (dr_0 ** 2) / (2 * nLine)
    # Set every half-th point (one per line) to v0
    v[half::N] = v0

    return v
