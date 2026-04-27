from src.geom1.bmVolumeElement1 import bmVolumeElement1
from src.traj123.bmTraj_lineDirection import bmTraj_lineDirection
from src.traj123.bmTraj_lineReshape import bmTraj_lineReshape
from src.traj123.bmTraj_squaredNorm import bmTraj_squaredNorm
import numpy as np
from src.arrayUtility.arrayUtility import bmBlockReshape

def bmVolumeElement_center_out_radial3(t):
    if not (len(t.shape) == 3 and t.shape[0] == 3):
        raise ValueError("The trajectory must be 3Dim")

    centerFlag = False
    if np.linalg.norm(t[:, :, 0]) < (100 * np.finfo(float).eps):
        centerFlag = True
        t = t[:, :, 1:]

    t       = bmTraj_lineReshape(t)
    imDim   = t.shape[0]
    N       = t.shape[1]
    nLine   = t.shape[2]
    e = bmTraj_lineDirection(t)

    dr = np.zeros((N, nLine))
    for i in range(nLine):
        dr[:, i] = np.sum(t * e[:, i], axis=(0, 1))
    dr = bmVolumeElement1(dr)

    r_1 = np.zeros((1,) + t.shape[2:])
    for d in range(imDim):
        r_1 += (t[d, :, :] ** 2).ravel()
    r_1 = np.sqrt(r_1)
    r_1 = r_1.ravel().T

    r_2 = np.zeros((1,) + t.shape[2:])
    for d in range(imDim):
        r_2 += (t[d, :, :] ** 2).ravel()
    r_2 = np.sqrt(r_2)
    r_2 = r_2.ravel().T

    if centerFlag:
        dr[0, :] = r_2 / 2
    else:
        dr[0, :] = (r_1 + r_2) / 2

    ds = 4 * np.pi * bmTraj_squaredNorm(t) / nLine

    v = dr[0, :].reshape(-1, 1) * ds.reshape(-1, 1)
    if centerFlag:
        dr_0 = np.mean(r_1 / 2, axis=1)
        v0 = (4/3) * np.pi * (dr_0 ** 3)
        v = np.concatenate((v0, v))

    return v.ravel()
