import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape


def bmTraj_squaredNorm(t):
    mySize = np.array(np.shape(t))  # e.g. [3, N, nLine]
    t = bmPointReshape(t)           # [imDim, nPt]

    mySquaredNorm = np.zeros((1, t.shape[1]))
    for i in range(int(mySize[0])):
        mySquaredNorm += t[i, :] ** 2

    # Use F order to match MATLAB's column-major reshape convention.
    mySquaredNorm = mySquaredNorm.reshape([1] + list(mySize[1:]), order='F')
    return mySquaredNorm
