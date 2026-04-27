from src.arrayUtility.bmOne import bmOne
from src.arrayUtility.bmType import bmType
from src.arrayUtility.bmZero import bmZero
from src.gridding123.m.bmGut_partialCartesian import bmGut_partialCartesian
from src.traj1.bmTraj_cartesian1_lineAssym2 import bmTraj_cartesian1_lineAssym2
from src.traj123.bmTraj_partialCartesian_ind_u import bmTraj_partialCartesian_ind_u
from src.traj2.bmTraj_cartesian2_lineAssym2 import bmTraj_cartesian2_lineAssym2
from src.traj3.bmTraj_cartesian3_lineAssym2 import bmTraj_cartesian3_lineAssym2
import numpy as np


def bmUnionOfMriData_partialCartesian(y_cell, t_cell, N_u, dK_u):
    y_cell = y_cell.ravel()
    t_cell = t_cell.ravel()
    N_u = N_u.ravel().T
    dK_u = dK_u.ravel().T

    nCell = np.shape(y_cell, 1)
    imDim = np.shape(N_u.ravel(), 1)
    myType = bmType(y_cell[1])
    x = bmZero([np.prod(N_u.ravel()), nCell], myType)
    w = bmZero([np.prod(N_u.ravel()), 1], myType)

    for i in range(nCell):
        ind_u = bmTraj_partialCartesian_ind_u(t_cell[i], N_u, dK_u)

        nPt_i = np.shape(y_cell[i], 1)
        myOne = bmOne([nPt_i, 1], myType)

        w = w + bmGut_partialCartesian(myOne, ind_u, N_u)
        x = x + bmGut_partialCartesian(y_cell[i], ind_u, N_u)

    w = w.ravel()
    zero_mask = (w.ravel() == 0)
    one_mask = (w.ravel() > 0)
    w[zero_mask] = 1

    w = np.repeat(w.reshape(-1, 1), nCell, axis=1)
    x = x / w

    if imDim == 1:
        t = bmTraj_cartesian1_lineAssym2(N_u, dK_u)
    elif imDim == 2:
        t = bmTraj_cartesian2_lineAssym2(N_u, dK_u)
    elif imDim == 3:
        t = bmTraj_cartesian3_lineAssym2(N_u, dK_u)

    t = t[:, one_mask]

    if len(varargout) > 1:
        varargout[0] = t
    if len(varargout) > 2:
        check_if_full = (np.sum(one_mask) == np.prod(N_u))
        varargout[1] = check_if_full

    return x, varargout
