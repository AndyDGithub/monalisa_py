from src.image123.bmImResize import bmBlockReshape  # Import bmBlockReshape from arrayUtility module
import numpy as np

from src.image123.bmImSqueeze import bmImSqueeze

def bmImExtend(argIm, nPix):
    outIm = argIm

    [sqIm, imDim, imSize, s1, s2, s3] = bmImSqueeze(argIm)

    if imDim == 1:
        outIm = np.zeros((s1 + 2*nPix, 1))
        outIm[nPix+1 : nPix + s1, 0] = sqIm
    elif imDim == 2:
        outIm = np.zeros(imSize + 2*nPix)
        outIm[nPix+1 : nPix+s1, nPix+1 : nPix+s2] = sqIm
    elif imDim == 3:
        outIm = np.zeros((imSize + 2*nPix) + (2*nPix, s2, s3))
        outIm[nPix+1 : nPix+s1, nPix+1 : nPix+s2, nPix+1 : nPix+s3] = sqIm

    return outIm
