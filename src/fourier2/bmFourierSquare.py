import numpy as np
from third_part.matlab_compat.matlab_native import permute

def bmFourierSquare(argK, argEdge, varargin):
    a = 0
    b = 0

    if isinstance(argEdge, (int, float)):
        a = argEdge
        b = argEdge
    elif len(argEdge) == 2:
        a = argEdge[0]
        b = argEdge[1]
    else:
        raise ValueError("Wrong list of arguments. ")
        return

    if a <= 0 or b <= 0:
        raise ValueError("Wrong list of arguments. ")
        return

    if argK.shape[0] != 2 and argK.shape[1] != 2:
        raise ValueError('Wrong list of arguments')
        return

    myCenter = varargin[0].ravel() if len(varargin) > 0 else np.array([0, 0])
    myMachineEpsilon = 2 * np.finfo(float).eps

    myPerm = list(range(argK.ndim))
    if argK.shape[0] == 2:
        k = argK
    elif argK.shape[1] == 2:
        myPerm[0], myPerm[1] = 1, 0
        k = permute(argK, myPerm)

    k_size = np.array(k.shape)
    mySize = [2] + list(np.cumprod(k_size[1:]))

    k0 = np.reshape(k, mySize)

    myX = np.sin(np.pi * k0[0, :] * a) / (np.pi * k0[0, :])
    myY = np.sin(np.pi * k0[1, :] * b) / (np.pi * k0[1, :])

    myX[np.abs(k0[0, :]) < myMachineEpsilon] = a
    myY[np.abs(k0[1, :]) < myMachineEpsilon] = b

    if not np.array_equal(myCenter, [0, 0]):
        myI = complex(0, 1)
        myX *= np.exp(myI * 2 * np.pi * myCenter[0] * k0[0, :])
        myY *= np.exp(myI * 2 * np.pi * myCenter[1] * k0[1, :])

    out = myX * myY

    if argK.shape[0] == 2 and argK.shape[1] == 2:
        out = out.reshape([1, -1])
    elif argK.shape[0] > 2 and argK.shape[1] == 2:
        out = out.reshape([1, -1]) * np.ones(k_size[2:])
    elif argK.shape[0] == 2 and argK.shape[1] > 2:
        out = out.reshape([-1, 1]) * np.ones((1,) + k_size[2:])
    else:
        out = out.reshape(k_size[2:] + [-1, 1])

    return out
