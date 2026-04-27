import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape

def bmTraj_fullRadial2_lineAssym2(N, nSeg, dK_n):
    kMax = N * dK_n / 2
    lineAssym = 2

    phi = np.linspace(0, 2 * np.pi, nSeg + 1)
    phi = phi[1:nSeg]  # Remove the last redundant value (phi(end))

    r = np.arange(N) - N // 2 + lineAssym  # Corresponds to 'fix(N/2) + myShift' in MATLAB
    r *= kMax / (N // 2)

    myTraj = np.zeros((N, nSeg, 2))

    myTraj[:, :, 0] = r * np.cos(phi)
    myTraj[:, :, 1] = r * np.sin(phi)

    myTraj = bmBlockReshape(myTraj, [N * nSeg, 2]).T

    return myTraj
