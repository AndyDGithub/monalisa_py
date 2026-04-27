from src.fourierN.bmIDF import bmIDF
from third_part.matlab_compat.matlab_native import permute
from third_part.twix_for_monalisa.mapVBVD_JH_for_monalisa import mapVBVD_JH_for_monalisa


def bmTwix_getFirstProjOfShot(argFile, p):
    myTwix = mapVBVD_JH_for_monalisa(argFile)
    if isinstance(myTwix, list) and len(myTwix) > 0:
        myTwix = myTwix[-1]

    y_raw = myTwix.image.unsorted()
    y_raw = permute(y_raw, [2, 1, 3])
    nLine = myTwix.image.NLin
    if not (p is None or hasattr(p, 'nShot')):
        nShot = p.nShot
    else:
        nShot = myTwix.image.NSeg

    nSeg = nLine / nShot
    mySize = np.shape(y_raw)
    mySize = mySize.ravel().T
    y_raw = np.reshape(y_raw, [mySize[0], mySize[1], nSeg, nShot])

    myLineList = bmIDF(y_raw[:, :, 1, :], 1, [], 2)
    return myLineList
