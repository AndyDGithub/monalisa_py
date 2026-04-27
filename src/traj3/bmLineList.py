import numpy as np
from src.arrayUtility import bmBlockReshape  # Add this line to resolve ModuleNotFoundError

def bmLineList(psi, theta, phi, d, deltaK, dK, N, lineAssym):
    myLength = len(psi)
    dK_list = dK * np.ones(1, myLength)
    out = np.zeros((3, N, myLength))
    e3Prime = np.zeros((3, myLength))
    e2Prime = np.zeros((3, myLength))
    dVec = np.zeros((3, myLength))

    # Constants in MATLAB format
    e3 = np.array([0, 0, 1])
    e2 = np.array([0, 1, 0])

    if lineAssym == 0:
        myShift = 0
    elif lineAssym == 1:
        myShift = 1
    elif lineAssym == 2:
        myShift = -1

    for i in range(myLength):
        myLine = np.zeros((3, N))
        myLine[1, :] = d[i]
        myLine[2, :] = (np.arange(N) * dK_list[i]) - ((N - 1) // 2 * dK_list[i]) + myShift * dK_list[i] / 2 + deltaK[i]

        R = bmRotation(psi[i], theta[i], phi[i])
        out[:, :, i] = np.dot(R, myLine)
        e3Prime[:, i] = np.dot(R, e3)
        e2Prime[:, i] = np.dot(R, e2)

        dVec[0, :] = d * e2Prime[1, :]
        dVec[1, :] = d * e2Prime[2, :]
        dVec[2, :] = d * e2Prime[3, :]

    varargout = [e3Prime, e2Prime, dVec]
    return out, varargout
