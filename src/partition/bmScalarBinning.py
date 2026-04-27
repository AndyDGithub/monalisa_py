import numpy as np
from src.arrayUtility import bmBlockReshape  # Import the required function from 'src.arrayUtility'

def bmScalarBinning(x, nBin):
    x = x.ravel().T
    N = np.shape(x, 2)
    myBinLength = int(np.floor(N / nBin))

    myMask = np.zeros((nBin, N), dtype=bool)

    for i in range(nBin):
        myMask[i, i * myBinLength:(i + 1) * myBinLength] = True

    myMask[-1, -myBinLength:] = True

    perm_indices = np.argsort(np.arange(N))
    inv_perm_indices = np.argsort(perm_indices)
    myMask = myMask[:, inv_perm_indices]

    return myMask
