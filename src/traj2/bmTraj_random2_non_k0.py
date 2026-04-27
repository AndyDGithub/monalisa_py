import numpy as np
from third_part.matlab_compat.matlab_native import double

def bmTraj_random2_non_k0(nPt, N_u, dK_u):
    myEps = 100 * np.finfo(float).eps  # -------------------------------------------------------- magic_number

    N_u = double(N_u.ravel().T)
    dK_u = double(dK_u.ravel().T)
    lx = (N_u[0, 0] - 1) * dK_u[0, 0]
    ly = (N_u[0, 1] - 1) * dK_u[0, 1]
    sx = N_u[0, 0] / 2 * dK_u[0, 0]
    sy = N_u[0, 1] / 2 * dK_u[0, 1]

    x = (np.random.rand(1, nPt) * lx) - sx
    y = (np.random.rand(1, nPt) * ly) - sy

    t = np.vstack((x.flatten(), y.flatten())).T

    n = np.sqrt(t[:, 0]**2 + t[:, 1]**2)
    m = (n < myEps)
    while np.sum(m) > 0:
        new_x = np.random.rand(nPt) * lx - sx
        new_y = np.random.rand(nPt) * ly - sy
        new_n = np.sqrt(new_x**2 + new_y**2)

        t[~m, :] = np.vstack((new_x[~m], new_y[~m])).T
        n[~m] = new_n[~m]
        m = (n < myEps)

    if len(t) != nPt:
        raise ValueError("The output traj has wrong size.")

    return t
