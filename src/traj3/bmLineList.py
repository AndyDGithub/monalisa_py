import numpy as np
from src.geom123 import bmTraj

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

# The output format is the lineOfPoint-format i.e. the size 
# is (3, N, numOfLines). 

def bmLineList(psi, theta, phi, d, deltaK, dK, N, lineAssym):
    """
    Compute line lists for given rotation angles and line parameters.

    Parameters
    ----------
    psi, theta, phi : array_like
        Rotation angles (in radians) for each line.
    d : array_like
        Distance between points along each line.
    deltaK : array_like
        Offset in k-space for each line.
    dK : float
        Step size in k-space.
    N : int
        Number of points per line.
    lineAssym : int
        Asymmetry flag:
            0 - no shift
            1 - positive half-step shift
            2 - negative half-step shift

    Returns
    -------
    out : ndarray, shape (3, N, numLines)
        Rotated line coordinates.
    e3Prime : ndarray, shape (3, numLines)
        Rotated z-axis unit vectors.
    e2Prime : ndarray, shape (3, numLines)
        Rotated y-axis unit vectors.
    dVec : ndarray, shape (3, numLines)
        Distance vectors along the rotated y-axis.
    """
    psi = np.asarray(psi, dtype=float)
    theta = np.asarray(theta, dtype=float)
    phi = np.asarray(phi, dtype=float)
    d = np.asarray(d, dtype=float)
    deltaK = np.asarray(deltaK, dtype=float)

    myLength = len(psi)
    dK_list = np.full(myLength, dK, dtype=float)

    out = np.zeros((3, N, myLength), dtype=float)
    e3Prime = np.zeros((3, myLength), dtype=float)
    e2Prime = np.zeros((3, myLength), dtype=float)

    e3 = np.array([0.0, 0.0, 1.0])
    e2 = np.array([0.0, 1.0, 0.0])

    if lineAssym == 0:
        myShift = 0
    elif lineAssym == 1:
        myShift = 1
    elif lineAssym == 2:
        myShift = -1
    else:
        raise ValueError("lineAssym must be 0, 1, or 2")

    for i in range(myLength):
        myLine = np.zeros((3, N), dtype=float)
        myLine[1, :] = d[i]
        myLine[2, :] = (
            np.arange(N) * dK_list[i]
            - ((N - 1) / 2.0) * dK_list[i]
            + myShift * dK_list[i] / 2.0
            + deltaK[i]
        )

        R = bmTraj.bmRotation(psi[i], theta[i], phi[i])
        out[:, :, i] = R @ myLine
        e3Prime[:, i] = R @ e3
        e2Prime[:, i] = R @ e2

    dVec = np.zeros((3, myLength), dtype=float)
    dVec[0, :] = d * e2Prime[0, :]
    dVec[1, :] = d * e2Prime[1, :]
    dVec[2, :] = d * e2Prime[2, :]

    return out, e3Prime, e2Prime, dVec
