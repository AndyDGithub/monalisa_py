import numpy as np
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape from arrayUtility module


def bmVolumeElement_replace_cartesian(arg_v, N_u):
    v = arg_v

    imDim = np.shape(N_u.ravel(), 1)
    v = np.reshape(v, N_u)

    if imDim == 1:
        v = v.ravel()

        v = bmBlockReshape(v, (2, v.size - 2), [0, 1])
    elif imDim == 2:
        v = np.reshape(v, (-1, imDim * imDim))
        v = bmBlockReshape(v, (3, imDim * imDim - 2), [0, 1, 2])
        v = np.reshape(v, (imDim, imDim, -1))
    elif imDim == 3:
        v = np.reshape(v, (-1, imDim * imDim * imDim))
        v = bmBlockReshape(v, (4, imDim * imDim * imDim - 2), [0, 1, 2, 3])
        v = np.reshape(v, (imDim, imDim, imDim, -1))

    return v
