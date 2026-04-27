from third_part.matlab_compat.matlab_native import permute
import numpy as np

def bmFourierSphere(argK, argR, varargin):
    if argK.shape[0] != 3 and argK.shape[1] != 3:
        raise ValueError("Wrong list of arguments")
    if argR <= 0:
        raise ValueError("Wrong list of arguments.")

    myMachineEpsilon = 1e-15
    myCenter = varargin[1] if len(varargin) > 1 else np.array([0, 0, 0])

    if argK.shape[0] == 3:
        k = argK
    elif argK.shape[1] == 3:
        k = permute(argK, [1, 0])

    k_size = np.shape(k)
    mySize = np.array([3, np.prod(k_size[1:])])
    k0 = np.reshape(k, mySize)
    k0_norm = np.sqrt(np.sum(k0**2, axis=0))

    k1_norm = 2 * np.pi * k0_norm * argR
    myPhase = np.exp(-1j * 2 * np.pi * np.dot(myCenter, k0))

    out = 4 * np.pi * argR**3 * np.ones(np.shape(k0_norm))
    out *= ((np.sin(k1_norm) - k1_norm * np.cos(k1_norm)) / (k1_norm**3)) * myPhase
    out[k0_norm < myMachineEpsilon] = 4/3 * np.pi * argR**3

    if len(argK.shape) == 2 and argK.shape[0] == 3:
        out = out.reshape([1, np.size(out)])
    elif len(argK.shape) == 2 and argK.shape[1] == 3:
        out = out.reshape([np.size(out), 1])
    elif len(argK.shape) > 2 and argK.shape[0] == 3:
        out = out.reshape([1, *k_size[1:]])
    elif len(argK.shape) > 2 and argK.shape[1] == 3:
        out = out.reshape([*k_size[1:], 1])

    return out
