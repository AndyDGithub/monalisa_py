import numpy as np
from third_part.matlab_compat.matlab_native import permute
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Import statement for missing function

def bmFourierDisc(argK, argR, varargin=None):
    if argK.shape[0] != 2 and argK.shape[1] != 2:
        raise ValueError("Wrong list of arguments")

    if argR <= 0:
        raise ValueError("Wrong list of arguments.")

    myMachineEpsilon = 1e-15

    if varargin is not None:
        myCenter = np.array(varargin[0]).reshape([2, 1])
    else:
        myCenter = np.array([0, 0]).reshape([2, 1])

    k = argK
    if k.shape[0] != 2 and k.shape[1] == 2:
        myPerm = [1, 0]
        k = permute(k, myPerm)

    k_size = np.shape(k)
    mySize = [2, np.prod(k_size[1:])]

    k0 = np.reshape(k, mySize)
    k0_norm = np.sqrt(k0[0, :] ** 2 + k0[1, :] ** 2)
    k1_norm = 2 * np.pi * k0_norm * argR

    myPhase = np.exp(1j * 2 * np.pi * myCenter.T @ k0)
    out = 2 * np.pi * argR ** 2 * np.ones((np.shape(k0_norm)))

    out *= (np.special.jv(1, k1_norm) / k1_norm) * myPhase

    out[k0_norm < myMachineEpsilon] = np.pi * argR ** 2

    if len(argK.shape) == 2 and argK.shape[0] == 2:
        out = np.reshape(out, [1, np.size(out)])
    elif len(argK.shape) == 2 and argK.shape[1] == 2:
        out = np.reshape(out, [np.size(out), 1])
    elif len(argK.shape) > 2 and argK.shape[0] == 2:
        out = np.reshape(out, [1, *k_size[1:]])
    elif len(argK.shape) > 2 and argK.shape[1] == 2:
        out = np.reshape(out, [k_size[0], 1, *k_size[2:]])

    return out
