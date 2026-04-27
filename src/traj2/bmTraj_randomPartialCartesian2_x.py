import numpy as np
from third_part.matlab_compat.matlab_native import repmat

def bmTraj_randomPartialCartesian2_x(N_u, dK_u, myPerOne):
    N_u = N_u.ravel().T
    dK_u = dK_u.ravel().T

    Nx = N_u[0]
    Ny = N_u[1]
    dKx = dK_u[0]
    dKy = dK_u[1]

    kx = np.arange(-Nx / 2, Nx / 2, dtype=float) * dKx
    ky = np.arange(-Ny / 2, Ny / 2, dtype=float) * dKy

    m = (np.random.rand(1, Ny) <= myPerOne)
    nLine = np.sum(m.ravel())
    ky = ky[m]
    kx = repmat(kx, [1, nLine])
    ky = repmat(ky.T, [Nx, 1])

    t = np.concatenate((kx.flatten(), ky.flatten()))

    return t
