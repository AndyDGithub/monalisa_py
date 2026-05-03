from third_part.matlab_compat.matlab_native import permute
import numpy as np

def bmTwix_getCenterOfLine(argFile):
    myTwix = mapVBVD_JH_in_bmToolBox(argFile)

    # If iscell(myTwix)
    if isinstance(myTwix, list):
        myTwix = myTwix[-1]

    y_raw = myTwix.image.unsorted()
    y_raw = permute(y_raw, [2, 1, 3])
    
    nShot          = myTwix.image.NSeg
    nLine          = myTwix.image.NLin
    nSeg           = nLine / nShot
    
    mySize = np.shape(y_raw)
    mySize = mySize[::-1]
    y_raw  = np.reshape(y_raw, [mySize[0], mySize[1], nSeg, nShot])
    
    N = np.shape(y_raw, 2)
    myCenter = y_raw[:, N // 2 + 1, :, :]
    myCenter = np.reshape(myCenter, [mySize[0], nLine])
    
    return myCenter
