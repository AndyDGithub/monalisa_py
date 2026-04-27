import numpy as np
from src.arrayUtility import bmBlockReshape

def bmSimbaCluster_to_lineMask(simbaCluster, nSeg, nShot):
    nMask = np.shape(simbaCluster)[0]
    lineMask = np.zeros((nMask, nSeg, nShot), dtype=bool)

    for i in range(nMask):
        lineMask[i, :, simbaCluster[i]] = True

    return lineMask
