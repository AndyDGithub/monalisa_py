from src.varargin.bmVarargin import bmVarargin
import numpy as np

from third_part.matlab_compat.matlab_native import single


def bmImConv_byShiftList(argIm, argShiftList, varargin):
    # varargin
    [myKernelVal, nIter] = bmVarargin(varargin)
    myKernelVal = np.ones((np.shape(argShiftList, 1), 1))
    nIter = 1 if nIter is None else nIter

    argSize = np.shape(argIm)
    mySize = argSize.ravel().T
    out_1 = single(argIm).reshape(-1)
    mySize = np.shape(out_1)
    out_2 = np.zeros(mySize, "single")
    nShift = np.shape(argShiftList, 1)

    for _ in range(nIter):
        for j in range(nShift):
            out_2 += np.roll(out_1, argShiftList[j]) * myKernelVal[j]
        out_1 = out_2 / nShift
        out_2 = np.zeros(mySize, "single")

    return out_1.reshape(argSize)
