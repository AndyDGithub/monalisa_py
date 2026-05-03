import numpy as np

def bmPhaseLift1(argSignal, myLift=2 * np.pi):
    """
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023

    Applies a phase lift algorithm to the input signal.

    Parameters
    ----------
    argSignal : array_like
        The input signal.
    myLift : float, optional
        Lifting value. Defaults to 2*pi.

    Returns
    -------
    out : ndarray
        The processed signal after applying the phase lift algorithm.
    """
    argSignalSize = np.shape(argSignal)
    mySignal = np.squeeze(argSignal)
    mySize = np.shape(mySignal)

    # Reshape to 2-D matrix: (rows, columns)
    mySignal = mySignal.reshape((mySize[0], np.prod(mySize[1:])))
    mySize = mySignal.shape

    myTransposeFlag = False

    if mySize[0] < 2 and mySize[1] < 2:
        return mySignal.reshape(argSignalSize)

    if mySize[0] < 2 and mySignal.ndim == 2:
        mySignal = mySignal.T
        flipTemp = mySize[1]
        mySize = (mySize[0], flipTemp)
        myTransposeFlag = True

    for i in range(1, mySize[0]):
        diff = mySignal[i, :] - mySignal[i - 1, :]
        myMask = np.abs(diff) > myLift / 2

        myValPlus = np.abs(mySignal[i, :] + myLift - mySignal[i - 1, :])
        myValMinus = np.abs(mySignal[i, :] - myLift - mySignal[i - 1, :])

        myMaskPlus = (myValPlus < myValMinus) & myMask
        myMaskMinus = (myValMinus < myValPlus) & myMask

        mySignal[i:, :] += myMaskPlus[:, None] * myLift
        mySignal[i:, :] -= myMaskMinus[:, None] * myLift

    if myTransposeFlag:
        mySignal = mySignal.T
        flipTemp = mySize[1]
        mySize = (mySize[0], flipTemp)

    return mySignal.reshape(argSignalSize)

# src/geom123/__init__.py
# Stub for bmTraj to satisfy imports

def bmTraj(*args, **kwargs):
    """
    Placeholder for bmTraj. Returns None.
    """
    return None

# End of file
