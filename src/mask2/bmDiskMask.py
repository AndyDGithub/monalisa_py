import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Import bmBlockReshape function from arrayUtility module


def bmDiskMask(argSize, argCenter, argRadius):
    argSize = np.ravel(argSize).T
    argCenter = np.ravel(argCenter).T
    myRadius_squared = argRadius ** 2

    x, y = bmBlockReshape(np.indices(argSize), block_size=(1, 1))

    myMask = ( (x - argCenter[0])**2 + (y - argCenter[1])**2 ) <= myRadius_squared
    myMask = np.reshape(myMask, argSize)

    return myMask
