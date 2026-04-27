from third_part.matlab_compat.matlab_native import double
import numpy as np

def bmTraj_random2_k0(nPt, N_u, dK_u):
    myEps = 100 * np.finfo(float).eps  # Adjusting magic_number to Python's equivalent

    N_u     = double(N_u.ravel().T)
    dK_u    = double(dK_u.ravel().T)

    lx = (N_u[0, 0] - 1) * dK_u[0, 0]
    ly = (N_u[0, 1] - 1) * dK_u[0, 1]
    sx = N_u[0, 0] / 2 * dK_u[0, 0]
    sy = N_u[0, 1] / 2 * dK_u[0, 1]

    x = (np.random.rand(1, nPt) * lx) - sx
    y = (np.random.rand(1, nPt) * ly) - sy

    t = np.vstack((x.ravel(), y.ravel()))

    n = np.sqrt(t[0, :] ** 2 + t[1, :] ** 2)
    m = (n < myEps)

    if sum(m) == 0:
        t = np.vstack(([0, 0], t[:, :-1]))

    if len(t[0]) != nPt:
        raise ValueError('The output traj has wrong size.')

    return t
