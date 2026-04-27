import numpy as np
from src.arrayUtility import bmBlockReshape  # Import required module

def bmPhaseLift1(argSignal, varargin):
    argSignalSize = np.shape(argSignal)
    mySignal = np.squeeze(argSignal)
    mySize = np.shape(mySignal)

    out = np.reshape(mySignal, argSignalSize)

    if mySize[0] < 2 and mySize[1] < 2:
        return out

    elif mySize[0] < 2 and mySignal.ndim == 2:
        mySignal = mySignal.T
        flipTemp = mySize[1]
        mySize[1], mySize[0] = mySize[0], flipTemp
        out = np.reshape(mySignal, argSignalSize)

    if len(varargin) > 0:
        myLift = varargin[0]
    else:
        myLift = 2 * np.pi

    for i in range(1, mySize[0]):
        myMask = np.abs(mySignal[i, :] - mySignal[i-1, :]) > myLift / 2

        myValPlus = np.abs(mySignal[i, :] + myLift - mySignal[i-1, :])
        myValMinus = np.abs(mySignal[i, :] - myLift - mySignal[i-1, :])

        myMaskPlus = (myValPlus < myValMinus) * myMask
        myMaskMinus = (myValMinus < myValPlus) * myMask

        myMaskPlus = np.repeat(myMaskPlus, mySize[0] - i + 1, axis=0)
        myMaskMinus = np.repeat(myMaskMinus, mySize[0] - i + 1, axis=0)

        mySignal[i:end, :] += myMaskPlus * myLift
        mySignal[i:end, :] -= myMaskMinus * myLift

    if out.ndim == 2:
        mySignal = bmBlockReshape(mySignal, [1, -1])
    else:
        mySignal = np.reshape(mySignal, argSignalSize)

    return mySignal
