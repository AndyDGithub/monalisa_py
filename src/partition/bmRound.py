import numpy as np
from src.arrayUtility import bmBlockReshape  # Importing the required function


def bmRound(varargin):
    if len(varargin) == 1:
        return round(varargin[0])
    elif len(varargin) == 2:
        myVal = varargin[0]
        myValSize = np.shape(myVal)
        myVal = myVal.ravel().T

        myGridd = varargin[1]
        myGriddSize = np.shape(myGridd)
        myGridd = np.sort(myGridd.ravel())

        n = len(myVal)
        m = len(myGridd)

        myVal2 = np.repeat(myVal, [m, 1], axis=0)
        myGridd2 = np.repeat(myGridd, [1, n], axis=0)

        myDiff = (myVal2 - myGridd2)
        myAbs = np.abs(myDiff)

        _, myInd1 = np.min(myAbs, axis=0)
        _, myInd2 = np.min(np.flipud(myAbs), axis=0)
        myInd2 = m - myInd2 + 1

        myLineInd = myInd1 + (np.arange(n) * m)
        mySign = np.sign(myVal2[myLineInd])

        myInd = myInd1 * (mySign < 0) + myInd2 * (mySign >= 0)

        myRound = myGridd[myInd]
        out = np.reshape(myRound, myValSize)
    else:
        return []
