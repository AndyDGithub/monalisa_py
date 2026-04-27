from third_part.matlab_compat.matlab_native import double
import numpy as np

def bmTraj_random1_non_k0(nPt, N_u, dK_u):
    myEps = 100 * np.finfo(float).eps;  # -------------------------------------------------------- magic_number
    N_u     = double(N_u.ravel().T)
    dK_u    = double(dK_u.ravel().T)
    lx = (N_u[0, 0] - 1) * dK_u[0, 0]
    sx = N_u[0, 0] / 2 * dK_u[0, 0]
    x = np.random.rand(nPt) * lx - sx
    t = x.reshape(-1, 1)
    n = np.abs(t)
    m = (n < myEps)

    while np.sum(m) != 0:
        new_x = np.random.rand(nPt) * lx - sx
        new_n = np.abs(new_x)

        # Update indices where new values are too small
        new_m = (new_n < myEps)
        m[~m & new_m] = True

    t[~m] = new_x[~m].reshape(-1, 1)

    if t.shape[1] != nPt:
        raise ValueError("The output traj has wrong size.")

    return t
