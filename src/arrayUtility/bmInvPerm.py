import numpy as np


def bmInvPerm(myPerm):
    myPerm = np.array(myPerm).ravel().astype(int)
    myList = np.arange(len(myPerm))
    myList = myList[myPerm]
    return np.argsort(myList)
