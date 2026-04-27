import numpy as np


def bmMultiIndex2Index(argMultiInd, argSize):
    myMultiInd = np.array(argMultiInd).ravel().astype(int)
    mySize = np.array(argSize).ravel().astype(int)
    myMultiInd = myMultiInd - 1
    L = len(mySize)
    outInd = int(myMultiInd[0])
    for i in range(1, L):
        outInd += int(myMultiInd[i]) * int(np.prod(mySize[:i]))
    outInd = outInd + 1
    return outInd
