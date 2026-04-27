from src.arrayUtility.bmPointReshape import bmPointReshape
import numpy as np


def bmTraj_rescaleToUnitCube(t, N_u, dK_u):
    in_size = np.shape(t)
    t = bmPointReshape(t)
    t_out = t

    imDim = np.shape(N_u.ravel(), 1)
    if imDim > 0:
        t_out[0, :] /= (N_u[0, 0] * dK_u[0, 0])
    if imDim > 1:
        t_out[1, :] /= (N_u[0, 1] * dK_u[0, 1])
    if imDim > 2:
        t_out[2, :] /= (N_u[0, 2] * dK_u[0, 2])

    t_out = np.reshape(t_out, in_size)

    if np.max(t_out) > 0.5:
        print("The rescaled trajectory is out of the unit cube. The input trajectory may be wrong.")
    if np.min(t_out) < -0.5:
        print("The rescaled trajectory is out of the unit cube. The input trajectory may be wrong.")
    if np.max(t_out) < 0.5 - 3 * np.mean(dK_u):
        print("The rescaled trajectory does not fill the unit cube. The input trajectory may be wrong or a bad sampling.")
    if np.min(t_out) > -0.5 + 3 * np.mean(dK_u):
        print("The rescaled trajectory does not fill the unit cube. The input trajectory may be wrong or a bad sampling.")

    return t_out
