from third_part.matlab_compat.matlab_native import logical
import numpy as np

def bmBluryMaskExctract(argBluryMask, argArray):
    argBluryMask = argBluryMask.ravel().T
    argArray     = argArray.ravel().T

    # argArray = argArray * argBluryMask
    myMask = logical(argBluryMask)
    out = argArray[myMask]
    outSum = np.sum(argBluryMask)
    return (out, outSum)
