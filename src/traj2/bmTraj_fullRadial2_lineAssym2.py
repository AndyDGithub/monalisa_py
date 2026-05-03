import numpy as np

def bmTraj_fullRadial2_lineAssym2(N, nSeg, dK_n):
    """
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023
    """
    kMax = N * dK_n / 2
    lineAssym = 2

    if lineAssym == 0:
        myShift = 0
    elif lineAssym == 1:
        myShift = 1
    else:  # lineAssym == 2
        myShift = 0

    phi = np.linspace(0, 2 * np.pi, nSeg + 1)
    phi = phi[:-1]

    r = np.arange(N) - np.fix(N / 2) + myShift
    r = r * kMax / np.fix(N / 2)

    myTraj = np.zeros((N, nSeg, 2))

    myTraj[:, :, 0] = np.outer(r, np.cos(phi))
    myTraj[:, :, 1] = np.outer(r, np.sin(phi))

    myTraj = myTraj.reshape(N * nSeg, 2).T

    return myTraj
