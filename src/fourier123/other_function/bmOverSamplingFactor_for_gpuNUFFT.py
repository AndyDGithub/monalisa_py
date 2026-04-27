import numpy as np
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape to resolve ModuleNotFoundError

def bmOverSamplingFactor_for_gpuNUFFT(N_u, n_u):
    myOsf = []

    if np.allclose(N_u, n_u):
        myOsf = 1
        return myOsf

    N_u = N_u.ravel().T
    n_u = n_u.ravel().T
    imDim = np.shape(N_u.ravel(), 1)

    if imDim == 1:
        myOsf = N_u[0, 0] / n_u[0, 0]

    elif imDim == 2:
        myOsf_1 = N_u[0, 0] / n_u[0, 0]
        myOsf_2 = N_u[0, 1] / n_u[0, 1]

        if not np.isclose(myOsf_1, myOsf_2):
            raise ValueError("Oversampling for gpu_NUFFT must be isotropic.")
        else:
            myOsf = myOsf_1

    elif imDim == 3:
        myOsf_1 = N_u[0, 0] / n_u[0, 0]
        myOsf_2 = N_u[0, 1] / n_u[0, 1]
        myOsf_3 = N_u[0, 2] / n_u[0, 2]

        if not (np.isclose(myOsf_1, myOsf_2) and np.isclose(myOsf_1, myOsf_3)):
            raise ValueError("Oversampling for gpu_NUFFT must be isotropic.")
        else:
            myOsf = myOsf_1

    if not myOsf:
        raise ValueError('Problem in "bmOverSamplingFactor_for_gpuNUFFT"')

    return myOsf
