from src.arrayUtility.bmPointReshape import bmPointReshape
from src.traj1.bmTraj_cartesian1_lineAssym2 import bmTraj_cartesian1_lineAssym2
from src.traj2.bmTraj_cartesian2_lineAssym2 import bmTraj_cartesian2_lineAssym2
from src.traj3.bmTraj_cartesian3_lineAssym2 import bmTraj_cartesian3_lineAssym2
import numpy as np

def bmLowRes_cartesian(c, N_u_curr, dK_u_curr, N_u_new, dK_u_new):
    myEps = eps * 1e3  # --------------------------------------------------------- magic_number

    N_u_curr    = N_u_curr.ravel().T
    dK_u_curr   = dK_u_curr.ravel().T
    N_u_new     = N_u_new.ravel().T
    dK_u_new    = dK_u_new.ravel().T

    c           = bmPointReshape(c)
    imDim       = np.shape(N_u_curr, 1)

    t = None
    if imDim == 1:
        t = bmTraj_cartesian1_lineAssym2(N_u_curr, dK_u_curr)
    elif imDim == 2:
        t = bmTraj_cartesian2_lineAssym2(N_u_curr, dK_u_curr)
    elif imDim == 3:
        t = bmTraj_cartesian3_lineAssym2(N_u_curr, dK_u_curr)

    nPt = np.shape(t, 2)
    myMask = np.ones((1, nPt), dtype=bool)

    if imDim > 0:
        temp_t    = t[0, :] / dK_u_curr[0, 0]
        dK_temp   = dK_u_new[0, 0] / dK_u_curr[0, 0]
        L         = dK_temp * N_u_new[0, 0]
        temp_mask = (-L / 2 - myEps <= temp_t)
        temp_mask = temp_mask & (temp_t <= L / 2 - dK_temp + myEps)
        myMask    = myMask & temp_mask

    if imDim > 1:
        temp_t    = t[1, :] / dK_u_curr[0, 1]
        dK_temp   = dK_u_new[0, 1] / dK_u_curr[0, 1]
        L         = dK_temp * N_u_new[0, 1]
        temp_mask = (-L / 2 - myEps <= temp_t)
        temp_mask = temp_mask & (temp_t <= L / 2 - dK_temp + myEps)
        myMask    = myMask & temp_mask

    if imDim > 2:
        temp_t    = t[2, :] / dK_u_curr[0, 2]
        dK_temp   = dK_u_new[0, 2] / dK_u_curr[0, 2]
        L         = dK_temp * N_u_new[0, 2]
        temp_mask = (-L / 2 - myEps <= temp_t)
        temp_mask = temp_mask & (temp_t <= L / 2 - dK_temp + myEps)
        myMask    = myMask & temp_mask

    c_out = c[:, myMask]
    return c_out
