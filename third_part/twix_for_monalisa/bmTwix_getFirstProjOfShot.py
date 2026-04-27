from third_part.twix_for_monalisa.mapVBVD_JH_for_monalisa import mapVBVD_JH_for_monalisa
import numpy as np

from src.fourierN.bmIDF import bmIDF
from third_part.matlab_compat.matlab_native import permute


def bmTwix_getFirstProjOfShot(argFile):
    myTwix = mapVBVD_JH_for_monalisa(argFile)
    # if iscell(myTwix)
    myTwix = myTwix[::-1][0]  # In Python, end refers to the last index.
    y_raw = myTwix.image.unsorted()
    y_raw = permute(y_raw, [2, 1, 3])
    nShot = myTwix.image.NSeg
    nLine = myTwix.image.NLin
    nSeg = nLine / nShot
    mySize = np.shape(y_raw)
    mySize = mySize[::-1]  # Reverse the order of dimensions to match MATLAB's ravel().T
    y_raw = np.reshape(y_raw, [mySize[2], mySize[1], nSeg, nShot])
    # myLineList = squeeze(y_raw[:, :, 1, :]);
    myLineList = bmIDF(y_raw[:, :, 0, :], 1, [], 2)
    return myLineList
