from third_part.matlab_compat.matlab_native import permute
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Importing missing function

def bmFourierDoor(argK, argEdge, varargin):
    a = 0
    if len(argEdge) == 1:
        a = argEdge[0]
    else:
        raise ValueError("Wrong list of arguments. ")

    if a <= 0:
        raise ValueError("Wrong list of arguments. ")

    if len(argK.shape) != 1 and argK.shape[1] != 1:
        raise ValueError("Wrong list of arguments")

    myCenter = varargin[0] if varargin else 0
    myMachineEpsilon = 2 * np.finfo(float).eps  # Magic number

    k = argK if len(argK.shape) == 1 else permute(argK, (1, 0))
    k_size = np.shape(k)
    k0 = bmBlockReshape(k, [1, -1])

    myX = np.sin(np.pi * k0[0, :] * a) / (np.pi * k0[0, :])
    myX[np.abs(k0[0, :]) < myMachineEpsilon] = a

    if not np.isclose(myCenter, 0):
        myI = complex(0, 1)
        myX *= np.exp(myI * 2 * np.pi * myCenter * k0[0, :])

    out = myX
    if len(argK.shape) == 2 and argK.shape[0] == 1:
        out = out.reshape([1, -1])
    elif len(argK.shape) == 2 and argK.shape[1] == 1:
        out = out.reshape([-1, 1])
    elif len(argK.shape) > 2 and argK.shape[0] == 1:
        out = out.reshape([1, -1] + list(k_size[2:]))
    else:
        out = out.reshape([k_size[1], 1] + list(k_size[2:]))

    return out
