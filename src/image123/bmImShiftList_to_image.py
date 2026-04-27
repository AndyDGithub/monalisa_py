from src.varargin.bmVarargin import bmVarargin
from src.image123.bmImReshape import bmImReshape
import numpy as np

def bmImShiftList_to_image(argShiftList, varargin):
    [argSize, myValList] = bmVarargin(varargin)
    argSize = max(argShiftList.ravel()) - min(argShiftList.ravel())
    if len(argSize) == 1:
        argSize = [argSize[0], 1]
    elif len(argSize) == 2:
        argSize = [argSize[0], argSize[1]]
    elif len(argSize) == 3:
        argSize = [argSize[0], argSize[1], argSize[2]]
    myValList = np.ones((len(argShiftList), 1), dtype=np.float64) if myValList is None else myValList

    argSize = argSize.ravel().T
    nShift = len(argShiftList)

    out = np.zeros(argSize)
    [out, _, _] = bmImReshape(out)
    myCenter = np.fix((np.array(argSize) - 1) / 2 + 1)

    if out.ndim == 0:
        raise ValueError("The dimension proposed by argSize is zero")

    if out.ndim == 1:
        for i in range(nShift):
            myIndex_x = argShiftList[i, 0] + myCenter[0]
            out[myIndex_x] = myValList[i, 0]
    elif out.ndim == 2:
        for i in range(nShift):
            myIndex_x = argShiftList[i, 0] + myCenter[0]
            myIndex_y = argShiftList[i, 1] + myCenter[1]
            out[myIndex_x, myIndex_y] = myValList[i, 0]
    elif out.ndim == 3:
        for i in range(nShift):
            myIndex_x = argShiftList[i, 0] + myCenter[0]
            myIndex_y = argShiftList[i, 1] + myCenter[1]
            myIndex_z = argShiftList[i, 2] + myCenter[2]
            out[myIndex_x, myIndex_y, myIndex_z] = myValList[i, 0]

    return out
