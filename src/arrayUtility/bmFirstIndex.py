import numpy as np


def bmFirstIndex(argString, argVal, argVec):
    argVec = np.asarray(argVec).ravel()
    if argString == "equalTo":
        myMask = (argVec == argVal)
    elif argString == "smallerThan":
        myMask = (argVec < argVal)
    elif argString == "biggerThan":
        myMask = (argVec > argVal)
    elif argString == "smallerEqualThan":
        myMask = (argVec <= argVal)
    elif argString == "biggerEqualThan":
        myMask = (argVec >= argVal)
    else:
        raise ValueError("Unknown comparison: " + argString)
    indices = np.where(myMask)[0]
    if len(indices) == 0:
        return len(argVec)
    return int(indices[0])
