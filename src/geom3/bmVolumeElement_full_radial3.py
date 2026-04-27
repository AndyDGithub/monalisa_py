from src.geom1.bmVolumeElement1 import bmVolumeElement1
from src.traj123.bmTraj_lineDirection import bmTraj_lineDirection
from src.traj123.bmTraj_lineReshape import bmTraj_lineReshape
from src.traj123.bmTraj_squaredNorm import bmTraj_squaredNorm
import numpy as np


def bmVolumeElement_full_radial3(t):
    if not (np.shape(t, 0) == 3):
        raise ValueError("The trajectory must be 3Dim.")

    t = bmTraj_lineReshape(t)
    imDim = np.shape(t, 1)
    N = np.shape(t, 2)
    nLine = np.shape(t, 3)
    e = bmTraj_lineDirection(t)
    
    if (N / 2 - int(N / 2)) > 0:
        raise ValueError("The number of points per line must be even, because the 0 must be at index position N/2+1.")

    dr = np.zeros((N, nLine))
    for i in range(nLine):
        dr[:, i] = t[:, :, i].T @ e[:, i]
    dr = bmVolumeElement1(dr)
    
    ds = squeeze(4 * np.pi * bmTraj_squaredNorm(t) / (2 * nLine))

    dr_0 = np.mean(dr[N // 2 + 1, :], axis=0) / 2
    v0 = (4 / 3) * np.pi * (dr_0 ** 3) / (2 * nLine)
    
    v = dr[:, :] * ds

    v[0, N // 2 + 1:N:end] = v0

    return v
