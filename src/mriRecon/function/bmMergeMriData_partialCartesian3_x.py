from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.traj123.bmTraj_partialCartesian_ind_u import bmTraj_partialCartesian_ind_u
import numpy as np

def bmMergeMriData_partialCartesian3_x(y, t, N_u, dK_u):
    N_u = N_u.ravel().T
    dK_u = dK_u.ravel().T
    imDim = np.shape(N_u.ravel(), 1)

    if imDim != 3:
        raise ValueError("imDim must be equal to 3.")

    nPt = np.shape(t.ravel(), 1) / imDim
    nCh = np.shape(y.ravel(), 1) / nPt
    nx = N_u[0, 0]
    nLine = nPt // nx

    t = np.reshape(t, [imDim, nx, nLine])
    y = np.reshape(y, [nCh, nx, nLine])

    ind_u = bmTraj_partialCartesian_ind_u(t[1:3, 0, :], N_u[0, 1:3], dK_u[0, 1:3])
    ind_u = ind_u.ravel().T

    if nLine != np.shape(ind_u, 2):
        raise ValueError("Problem in 'bmMergeMriData_partialCartesian3_x'")

    y_out = complex(np.zeros(np.shape(y)), np.zeros(np.shape(y)))
    t_out = np.zeros(np.shape(t))
    available_list = np.ones((1, nLine), dtype=bool)
    myCount = 0

    for i in range(nLine):
        if available_list[0, i]:
            myCount += 1

            ind_u_curr = ind_u[0, i]
            lineMask = (ind_u_curr == ind_u)

            available_list[0, lineMask] = False

            y_curr = np.mean(y[:, :, lineMask], axis=2)

            y_out[:, :, myCount - 1] = y_curr
            t_out[:, :, myCount - 1] = t[:, :, i]

    y_out = y_out[:, :, :myCount]
    t_out = t_out[:, :, :myCount]

    y_out = bmBlockReshape(y_out)
    t_out = bmBlockReshape(t_out)

    return (y_out, t_out)
