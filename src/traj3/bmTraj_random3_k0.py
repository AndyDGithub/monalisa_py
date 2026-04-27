from third_part.matlab_compat.matlab_native import double
import numpy as np

def bmTraj_random3_k0(nPt, N_u, dK_u):
    myEps = 100 * np.finfo(float).eps;  # -------------------------------------------------------- magic_number
    N_u     = double(N_u.ravel().T)
    dK_u    = double(dK_u.ravel().T)
    lx = (N_u[0, 0]-1)*dK_u[0, 0]
    ly = (N_u[0, 1]-1)*dK_u[0, 1]
    lz = (N_u[0, 2]-1)*dK_u[0, 2]
    sx = N_u[0, 0]/2*dK_u[0, 0]
    sy = N_u[0, 1]/2*dK_u[0, 1]
    sz = N_u[0, 2]/2*dK_u[0, 2]
    x = (np.random.rand(1, nPt)*lx) - sx
    y = (np.random.rand(1, nPt)*ly) - sy
    z = (np.random.rand(1, nPt)*lz) - sz

    t = np.concatenate((x.flatten(), y.flatten(), z.flatten()), axis=0)
    n = np.sqrt(t[0]**2 + t[1]**2 + t[2]**2)
    m = (n < myEps)

    if np.sum(m) == 0:
        t = np.concatenate(([0, 0, 0], t[:, :-1]), axis=0)

    if len(t[0]) != nPt:
        raise ValueError("The output traj has wrong size.")

    return t
