import numpy as np
from third_part.matlab_compat.matlab_native import permute

def bmFourierDisc(argK, argR, varargin=None):
    """
    Compute the Fourier disc kernel.

    Parameters
    ----------
    argK : np.ndarray
        Input array of any shape with one of the first two dimensions equal
equal to 2.
    argR : float
        Radius of the disc.
    varargin : list, optional
        Optional arguments; the first element (if provided) specifies the c
centre
        of the disc as a 2-element array.

    Returns
    -------
    np.ndarray
        Fourier disc kernel with the same dimensionality as the input.
    """
    argK = np.asarray(argK)
    if not (argK.shape[0] == 2 or argK.shape[1] == 2):
        raise ValueError("Wrong list of arguments")

    if argR <= 0:
        raise ValueError("Wrong list of arguments. ")

    # Centre handling
    if varargin and len(varargin) > 0:
        myCenter = np.asarray(varargin[0]).reshape(2, 1)
    else:
        myCenter = np.zeros((2, 1))

    # Bring the 2-dimension to the first axis
    if argK.shape[0] == 2:
        k = argK
    else:
        # Build a permutation that swaps axes 0 and 1
        perm = [1, 0] + list(range(2, argK.ndim))
        k = permute(argK, perm)

    # Flatten for vectorized computation
    k_flat = k.reshape(2, -1)

    k_norm = np.sqrt(np.sum(k_flat ** 2, axis=0))
    k1_norm = 2 * np.pi * k_norm * argR

    myPhase = np.exp(1j * 2 * np.pi * np.dot(myCenter.T, k_flat))

    out = 2 * np.pi * argR ** 2 * np.ones_like(k_norm)
    out = out * (np.special.jv(1, k1_norm) / k1_norm) * myPhase

    eps = 1e-15
    out[k_norm < eps] = np.pi * argR ** 2

    # Reshape to original dimensionality
    if argK.ndim == 2:
        if argK.shape[0] == 2:
            out = out.reshape(1, -1)
        else:
            out = out.reshape(-1, 1)
    else:
        if argK.shape[0] == 2:
            out = out.reshape(1, *argK.shape[1:])
        else:
            out = out.reshape(argK.shape[0], 1, *argK.shape[2:])

    return out
