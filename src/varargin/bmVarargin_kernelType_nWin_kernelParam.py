import numpy as np


def bmVarargin_kernelType_nWin_kernelParam(kernelType, nWin, kernelParam):
    """
    Set default values for kernelType, nWin, and kernelParam.

    Port of MATLAB bmVarargin_kernelType_nWin_kernelParam.m.

    Parameters
    ----------
    kernelType : str or None
    nWin       : int or None
    kernelParam: list/array or None

    Returns
    -------
    kernelType, nWin, kernelParam
    """
    if not isinstance(kernelType, str):
        kernelType = 'gauss'

    if nWin is None or (hasattr(nWin, '__len__') and len(nWin) == 0):
        nWin = 3

    if kernelParam is None or (hasattr(kernelParam, '__len__') and len(kernelParam) == 0):
        if kernelType == 'gauss':
            kernelParam = [0.61, 10]
        elif kernelType == 'kaiser':
            kernelParam = [1.95, 10, 10]
        else:
            kernelParam = [0.61, 10]

    nWin = float(np.float64(np.float32(nWin)))
    kernelParam = np.array(kernelParam, dtype=np.float64)
    kernelParam = np.float64(np.float32(kernelParam))

    if kernelType == 'gauss' and len(np.atleast_1d(kernelParam)) == 3:
        raise ValueError("Wrong number of gridding kernel parameters for 'gauss' (expected 2).")
    if kernelType == 'kaiser' and len(np.atleast_1d(kernelParam)) == 2:
        raise ValueError("Wrong number of gridding kernel parameters for 'kaiser' (expected 3).")

    return kernelType, nWin, kernelParam
