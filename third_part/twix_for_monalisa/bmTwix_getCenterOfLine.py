from third_part.twix_for_monalisa.mapVBVD_JH_for_monalisa import mapVBVD_JH_for_monalisa
import numpy as np
from scipy.ndimage import center_of_mass

def bmTwix_getCenterOfLine(argFile):
    myTwix = mapVBVD_JH_for_monalisa(argFile)
    # Ensure the returned object is not a cell array
    myTwix = myTwix[()]  # Assuming [] is used for squeezing in Python
    y_raw = myTwix.image.unsorted()
    nShot          = myTwix.image.NSeg
    nLine          = myTwix.image.NLin
    nSeg           = nLine/nShot
    mySize = np.shape(y_raw)
    y_raw  = np.reshape(y_raw, [mySize[1], mySize[0], nSeg, nShot])
    N = y_raw.shape[1]

    # Calculate the center of mass along the last two dimensions (axis=1)
    myCenter = center_of_mass(y_raw, labels=np.arange(nSeg), axis=(1, 2))

    return myCenter
