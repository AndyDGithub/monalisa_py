import numpy as np
from src.arrayUtility import bmBlockReshape

def bmVolumeElement_imDeformField2(vf, N_u):
    if not (len(vf) == 2):
        raise ValueError("The trajectory must be 2Dim.")

    N_u = N_u.ravel().T
    Nx_u = N_u[0]
    Ny_u = N_u[1]

    x_u = np.arange(Nx_u)
    y_u = np.arange(Ny_u)
    [x_u, y_u] = np.meshgrid(x_u, y_u)
    vf = np.reshape(vf, [2, int(np.prod(N_u))])

    t = np.concatenate((x_u[:, None] + vf[0, :], y_u[:, None] + vf[1, :]), axis=0).T
    s = t[:, 1:Nx_u-1, 1:Ny_u-1] \
       + t[:, 2:Nx_u   , 1:Ny_u-1] \
       + t[:, 1:Nx_u-1, 2:Ny_u   ] \
       + t[:, 2:Nx_u   , 2:Ny_u   ]
    s = s / 4

    a = s[:, :-1, :-1]
    b = s[:, 1:, :-1]
    c = s[:, :-1, 1:]
    d = s[:, 1:, 1:]

    a = np.concatenate((a, np.zeros((2, 1))), axis=1)
    b = np.concatenate((b, np.zeros((2, 1))), axis=1)
    c = np.concatenate((c, np.zeros((2, 1))), axis=1)
    d = np.concatenate((d, np.zeros((2, 1))), axis=1)

    v = (np.abs(np.cross(b - a, c - a)) + np.abs(np.cross(c - b, d - b))) / 2
    v = v[:, 1:-1, 1:-1]

    v = np.concatenate((v[0, :, :], v, v[-1, :, :]), axis=0)
    v = np.concatenate((v[:, 0, :], v, v[:, -1, :]), axis=1)

    return np.reshape(v, (1, int(np.prod(N_u))))
