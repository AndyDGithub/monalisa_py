import numpy as np
from src.arrayUtility import bmBlockReshape  # Add this line to resolve ModuleNotFoundError

def bmSparseMat_cell2line(argCell, varargin):
    myVararginFlag = False
    if len(varargin) > 0:
        myVararginFlag = True
        tempNumOfInd = np.array(varargin[0]).flatten()

    myLength = len(argCell)
    if not myVararginFlag:
        tempNumOfInd = np.zeros(myLength)
        for i in range(myLength):
            tempNumOfInd[i] = argCell[i].shape[1]

    tempNumOfInd_64 = tempNumOfInd.astype(np.int64)
    mySum_64 = np.sum(tempNumOfInd_64, axis=0, dtype=np.int64)  # This sum must be done in int64 !

    out = np.zeros((1, mySum_64.sum()), dtype=object)
    currentInd_1 = int64(1)
    currentInd_2 = int64(0)
    for i in range(1, myLength + 1):
        currentInd_2 += tempNumOfInd_64[i - 1]
        out[0, currentInd_1:currentInd_2] = argCell[i - 1].flatten()
        currentInd_1 = currentInd_2 + int64(1)

    return out
