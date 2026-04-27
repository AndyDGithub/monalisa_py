import numpy as np
from src.arrayUtility import bmBlockReshape

def bmTraj_random1_k0(nPt, N_u, dK_u):
    myEps = 100 * np.finfo(float).eps;  # ----------------------------------------------------------- magic_number

    t = np.random.rand(1, nPt) * (N_u * dK_u - dK_u) - N_u / 2 * dK_u
    t = np.sort(t.ravel()).reshape(-1, nPt)

    if np.sum(np.abs(t) < myEps) == 0:
        t = np.vstack((0, t[:, :nPt - 1]))

    if t.shape[1] != nPt:
        raise ValueError('The output traj has wrong size.')

    return t
