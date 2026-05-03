from __future__ import annotations

import numpy as np

def bmSparseMat_cell2line(argCell, *varargin):
    """
    Convert a list of matrices into a single line array.

    Parameters
    ----------
    argCell : list of numpy.ndarray
        List of 2-D arrays. Each array may have a different number of colum
columns.
    *varargin : tuple
        Optional argument that, if provided, supplies a list of column coun
counts
        that override the automatic determination from each array.

    Returns
    -------
    numpy.ndarray
        1-D array containing the column-wise flattened elements of each inp
input
        matrix concatenated together.
    """
    myVararginFlag = False
    if len(varargin) > 0:
        myVararginFlag = True
        tempNumOfInd = np.array(varargin[0]).flatten()
    else:
        myLength = len(argCell)
        tempNumOfInd = np.empty(myLength, dtype=int)
        for i in range(myLength):
            tempNumOfInd[i] = argCell[i].shape[1]

    tempNumOfInd_64 = tempNumOfInd.astype(np.int64)
    mySum_64 = np.sum(tempNumOfInd_64, dtype=np.int64)

    out = np.empty((1, mySum_64), dtype=object)
    currentInd_1 = 0
    currentInd_2 = 0
    for i in range(tempNumOfInd_64.size):
        currentInd_2 += tempNumOfInd_64[i]
        out[0, currentInd_1:currentInd_2] = argCell[i].ravel(order='F')
        currentInd_1 = currentInd_2

    return out
