import numpy as np

from src.geom1.bmVolumeElement1 import bmVolumeElement1
from src.geom123.bmVoronoi import bmVoronoi
from src.traj123.bmTraj_lineDirection import bmTraj_lineDirection
from src.traj123.bmTraj_lineReshape import bmTraj_lineReshape
from src.traj123.bmTraj_squaredNorm import bmTraj_squaredNorm


def bmVolumeElement_voronoi_full_radial3(t):
    if t.shape[0] != 3:
        raise ValueError("This function is for 3D trajectory only.")

    t = bmTraj_lineReshape(t)   # (3, N, nLine)
    N = t.shape[1]
    nLine = t.shape[2]

    e = bmTraj_lineDirection(t)  # (3, nLine)

    if N % 2 != 0:
        raise ValueError(
            "The number of points per line must be even "
            "(zero must be at index position N/2+1)."
        )

    # Radial projections: dr[k, i] = t[:, k, i] · e[:, i]
    dr = np.zeros((N, nLine))
    for i in range(nLine):
        dr[:, i] = t[:, :, i].T @ e[:, i]   # (N,3) @ (3,) -> (N,)

    dr = bmVolumeElement1(dr)   # (N, nLine)

    # Spherical surface areas via Voronoi
    ds = _bmSphericalVoronoi_1(t, 'half')   # (1, nLine)
    ds = np.tile(ds, (N, 1))                 # (N, nLine)

    sq_norm = bmTraj_squaredNorm(t)          # (1, N, nLine)
    ds = ds * sq_norm.squeeze(axis=0)        # (N, nLine)

    # Volume elements: flatten in Fortran (column-major) order to match MATLAB v = dr(:)'.*ds(:)'
    v = dr.ravel(order='F')[np.newaxis, :] * ds.ravel(order='F')[np.newaxis, :]  # (1, N*nLine)

    # Fix center volume elements (index N/2+1 in MATLAB = N//2 in Python 0-based)
    dr_0 = np.mean(dr[N // 2, :]) / 2
    center_indices = np.arange(N // 2, N * nLine, N)
    v[0, center_indices] = (4.0 / 3.0) * np.pi * (dr_0 ** 3) / (2 * nLine)

    return v


# ---------------------------------------------------------------------------
# Local helpers
# ---------------------------------------------------------------------------

def _bmSphericalVoronoi_1(t, half_or_full):
    imDim = t.shape[0]
    nLine = t.shape[2]

    # Last point of each line as sphere seeds: (3, nLine)
    s = t[:, -1, :]

    s_norm = np.sqrt(np.sum(s ** 2, axis=0, keepdims=True))  # (1, nLine)
    s = s / s_norm                                             # (3, nLine) normalised

    if half_or_full == 'half':
        s = np.concatenate([s, -s], axis=1)   # (3, 2*nLine)

    total = s.shape[1]
    myIndex = np.arange(total)

    # Six hemisphere partitions
    mask_p1 = s[0, :] >= 0;  s_p1 = s[:, mask_p1]; ind_p1 = myIndex[mask_p1]
    mask_m1 = s[0, :] <= 0;  s_m1 = s[:, mask_m1]; ind_m1 = myIndex[mask_m1]
    mask_p2 = s[1, :] >= 0;  s_p2 = s[:, mask_p2]; ind_p2 = myIndex[mask_p2]
    mask_m2 = s[1, :] <= 0;  s_m2 = s[:, mask_m2]; ind_m2 = myIndex[mask_m2]
    mask_p3 = s[2, :] >= 0;  s_p3 = s[:, mask_p3]; ind_p3 = myIndex[mask_p3]
    mask_m3 = s[2, :] <= 0;  s_m3 = s[:, mask_m3]; ind_m3 = myIndex[mask_m3]

    v_p1 = _bmSphericalVoronoi_2(s_p1[2, :], s_p1[1, :],  s_p1[0, :])
    v_m1 = _bmSphericalVoronoi_2(s_m1[2, :], s_m1[1, :], -s_m1[0, :])
    v_p2 = _bmSphericalVoronoi_2(s_p2[2, :], s_p2[0, :],  s_p2[1, :])
    v_m2 = _bmSphericalVoronoi_2(s_m2[2, :], s_m2[0, :], -s_m2[1, :])
    v_p3 = _bmSphericalVoronoi_2(s_p3[0, :], s_p3[1, :],  s_p3[2, :])
    v_m3 = _bmSphericalVoronoi_2(s_m3[0, :], s_m3[1, :], -s_m3[2, :])

    v = np.zeros((6, total))
    v[0, ind_p1] = v_p1
    v[1, ind_m1] = v_m1
    v[2, ind_p2] = v_p2
    v[3, ind_m2] = v_m2
    v[4, ind_p3] = v_p3
    v[5, ind_m3] = v_m3
    v = v[:, :nLine]   # first nLine columns (original hemisphere)

    myWeight = (v > 0).astype(float)
    denom = np.sum(myWeight, axis=0, keepdims=True)
    denom[denom == 0] = 1   # avoid division by zero
    v = np.sum(v, axis=0, keepdims=True) / denom   # (1, nLine)
    return v


def _bmSphericalVoronoi_2(s1, s2, s3):
    s = np.stack([np.asarray(s1).ravel(),
                  np.asarray(s2).ravel(),
                  np.asarray(s3).ravel()], axis=0)   # (3, nPt)
    nPt = s.shape[1]
    myIndex = np.arange(nPt)

    myAngle = np.arccos(1.0 / np.sqrt(3.0))
    myAngle = (np.pi / 2.0 - myAngle) / 3.0
    h1 = np.sin(1 * myAngle)
    h2 = np.sin(2 * myAngle)

    # Filter: remove points below h1
    keep = s[2, :] >= h1
    s = s[:, keep]
    myIndex = myIndex[keep]

    if s.shape[1] < 4:   # need at least 4 non-coplanar points for 2D Voronoi
        return np.zeros(nPt)

    myMask_2 = s[2, :] < h2

    # Project onto 2D plane (stereographic from top)
    p = s[0:2, :] / s[2:3, :]   # (2, nPt_filtered)

    myVoronoi = bmVoronoi(p, [False]).ravel()   # (nPt_filtered,)
    myVoronoi[myVoronoi <= 0] = 0.0
    myVoronoi[myMask_2] = 0.0
    myVoronoi = myVoronoi * np.abs(s[2, :] ** 3)

    out = np.zeros(nPt)
    out[myIndex] = myVoronoi
    return out
