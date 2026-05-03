import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape

from src.image123.bmImConv_inMask_byShiftList import bmNdim

def bmImPseudoDiffusion_inMask_byShiftList(argIm, argShiftList, argMask, varargin):
    nIter = []
    if len(varargin) > 0:
        nIter = varargin[1]
    if len(nIter) == 0:
        nIter = 1

    # initial
    argIm = np.array(argIm, dtype=np.single).squeeze()
    argMask = np.array(argMask, dtype=bool)
    argMask_neg = ~argMask
    myDim = bmNdim(argIm)
    if myDim == 1:
        argIm = argIm.ravel()
        argMask = argMask.ravel()
        argMask_neg = argMask_neg.ravel()

    argSize = np.shape(argIm)
    argSize = argSize.reshape(-1, order='F')

    out_1 = argIm
    out_1[argMask_neg] = 0

    nShift = np.shape(argShiftList)[0]

    # convolution
    for i in range(nIter):
        myZeroMask = (out_1 == 0)
        myZeroMask = bmBlockReshape(myZeroMask, argSize)

        myNonZeroMask = ~myZeroMask
        out_2 = np.zeros(argSize, dtype=np.single)
        myNumOfNonZero = np.zeros(argSize, dtype=np.single)
        for j in range(nShift):
            out_2 += np.roll(out_1, argShiftList[j])
            myNumOfNonZero += bmBlockReshape(myNonZeroMask, argSize)

        myNumOfNonZero[myNumOfNonZero == 0] = 1
        out_1 = out_2 / myNumOfNonZero

    out_1[argMask_neg] = 0
    out_1[argMask_neg] = np.reshape(np.array(argIm)[argMask_neg], argSize)

    return out_1
