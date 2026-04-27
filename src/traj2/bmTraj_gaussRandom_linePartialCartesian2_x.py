from third_part.matlab_compat.matlab_native import logical, repmat
import numpy as np
from src.arrayUtility import bmBlockReshape

def bmTraj_gaussRandom_linePartialCartesian2_x(N_u, dK_u, nLine, argSigma):
    N_u = N_u.ravel().T
    dK_u = dK_u.ravel().T

    Nx = N_u[0]
    Ny = N_u[1]
    dKx = dK_u[0]
    dKy = dK_u[1]

    kx = np.arange(-Nx/2, Nx/2 - 1) * dKx
    ky = np.arange(-Ny/2, Ny/2 - 1) * dKy

    mySigma = argSigma * Nx
    myMu = Nx / 2 + 1

    x = np.arange(1, Nx + 1)
    p = np.exp(-0.5*((x-myMu)/mySigma)**2)
    p /= np.sum(p)

    m = np.zeros((1, Nx))
    while np.sum(m) < nLine:
        myInd = int(np.round(1 + np.random.rand() * (Nx - 1)))
        if np.random.rand() <= p[0, myInd]:
            m[0, myInd] = 1

    m = logical(m).ravel()
    ky_filtered = ky[0, m]
    kx_repmat = repmat(kx, [1, nLine])
    ky_repmat = repmat(ky_filtered.T, [Nx, 1])

    t = np.concatenate((kx_repmat.ravel(), ky_repmat.ravel()))

    varargout = (t, m)
    return varargout
