"""Auto-generated from MATLAB source. Review manually before production use."""

import numpy as np
from scipy import signal

def bmAffinePhaseFit(argPhase, argX, varargin):
    argSize = np.shape(argPhase)
    myPhase = np.squeeze(argPhase)
    mySize = np.shape(myPhase)

    # Reshape for 2D
    myPhase = np.reshape(argPhase, (np.prod(mySize[:-1]), mySize[-1]))

    x = np.squeeze(argX)
    if len(x.shape) == 1:
        x = np.reshape(x, [1, -1])

    # Transpose if size is 2D (i.e., only one angle per point)
    if mySize[0] == 1:
        myPhase = myPhase.T
        mySize = np.shape(myPhase)

    cPhase = np.exp(1j * myPhase)
    myCenterMass = np.sum(cPhase, axis=1)
    myAngle = np.angle(myCenterMass)
    myAngle_table = np.repeat(myAngle[:, np.newaxis], mySize[1], axis=1)

    # Adjust phase to match center mass angle
    myPhase = np.mod(myPhase + np.pi - myAngle_table, 2*np.pi) - np.pi

    a_map = np.zeros((mySize[0],))
    b_map = np.zeros((mySize[0],))

    xTable = np.tile(x, (mySize[0], 1))
    zTable = myPhase

    MeanX = np.mean(xTable, axis=1)
    MeanZ = np.mean(zTable, axis=1)
    MeanX2 = np.mean(xTable**2, axis=1)
    MeanXZ = np.mean(xTable * zTable, axis=1)

    # Calculate offset and slope
    a_map = np.mod((MeanX2 * MeanZ - MeanX * MeanXZ) / (MeanX2 - MeanX**2) + myAngle, 2*np.pi) - np.pi
    b_map = np.mod((MeanXZ - MeanX * MeanZ) / (MeanX2 - MeanX**2), 2*np.pi)

    a_map_table = np.repeat(a_map[:, np.newaxis], x.shape[1], axis=1)
    b_map_table = np.repeat(b_map[:, np.newaxis], x.shape[1], axis=1)

    myFit = np.mod(a_map_table + b_map_table * xTable + np.pi, 2*np.pi) - np.pi

    if len(argSize) > 2:
        a_map = np.reshape(a_map, argSize[1:])
        b_map = np.reshape(b_map, argSize[1:])

    myFit = np.reshape(myFit, argSize)

    return (a_map, b_map, myFit)
