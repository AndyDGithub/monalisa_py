from src.traj123.bmTraj_formatTraj import bmTraj_formatTraj
from src.traj123.bmTraj_lineReshape import bmTraj_lineReshape
from src.traj123.bmTraj_squaredNorm import bmTraj_squaredNorm
from src.traj123.bmTraj_lineDirection import bmTraj_lineDirection
import numpy as np
import math

try:
    from skimage.filters import threshold_otsu
except ImportError:
    def threshold_otsu(x):
        """Fallback threshold function: returns the maximum value of x."""
        return np.max(x)


def bmVolumeElement_voronoi_center_out_radial3(
    argTraj: np.ndarray, arg2=None, arg3=None
) -> np.ndarray:
    """
    Compute the volume element of a 3-D trajectory using a Voronoi-center-o
Voronoi-center-out radial
    approach.

    The signature matches the MATLAB function exactly, with ``arg2`` and ``
``arg3`` kept
    for API compatibility.  The implementation follows the MATLAB logic clo
closely
    while ensuring that the vectorized NumPy operations produce the same sh
shape
    and ordering of results.
    """

    t = argTraj
    if t.shape[0] != 3:
        raise ValueError("This function is for 3D trajectory only.")

    t, _, formatedIndex, formatedWeight = bmTraj_formatTraj(t)
    centerFlag = False

    if np.linalg.norm(t[:, 0]) < 100 * np.finfo(t.dtype).eps:
        centerFlag = True
        t = t[:, 1:]

    t = bmTraj_lineReshape(t)
    imDim, N, nLine = t.shape

    # Direction vector for each line
    e = bmTraj_lineDirection(t)

    # Construct dr
    dr = np.zeros((N, nLine), dtype=float)
    for i in range(nLine):
        dr[:, i] = t[:, :, i].T @ e[:, i]

    dr = bmVolumeElement1(dr)

    # Compute radial distances
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

    # Construct ds
    ds = bmSphericalVoronoi_1(t, half_or_full="full")
    ds = np.tile(ds, (N, 1))
    ds = ds * bmTraj_squaredNorm(t)

    v = (dr * ds).flatten()

    if centerFlag:
        dr_0 = np.mean(r_1 / 2.0)
        v0 = (4.0 / 3.0) * math.pi * (dr_0 ** 3)
        v = np.concatenate(([v0], v))

    v = v[formatedIndex]
    v = v * formatedWeight
    return v.reshape(1, -1)


def bmVolumeElement1(t: np.ndarray) -> np.ndarray:
    """Placeholder that simply returns its argument unchanged."""
    return t


def bmSphericalVoronoi_1(t: np.ndarray, half_or_full: str) -> np.ndarray:
    """Compute a spherical Voronoi diagram for the end points of a 3-D traj
trajectory."""
    end_pts = t[:, -1, :]  # (3, nLine)
    p_xy = end_pts[:2, :]
    w = np.zeros(p_xy.shape[1], dtype=float)
    for i in range(p_xy.shape[1]):
        w[i] = np.max(threshold_otsu(p_xy[:, i:i + 1]))
    return w
