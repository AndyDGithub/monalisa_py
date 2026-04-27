import numpy as np


def bmIndex2MultiIndex(argInd, argSize):
    myInd = int(argInd) - 1
    mySize = np.array(argSize).ravel().astype(int)
    L = len(mySize)
    mySize_ext = np.concatenate(([1], mySize))
    P = np.zeros(L, dtype=int)
    for i in range(L):
        P[i] = int(np.prod(mySize_ext[:i + 1]))
    outInd = np.zeros(L, dtype=int)
    for i in range(L):
        j = L - 1 - i
        temp_ind = int(myInd // P[j])
        outInd[j] = temp_ind
        myInd = myInd - temp_ind * P[j]
    outInd = outInd + 1
    return outInd
