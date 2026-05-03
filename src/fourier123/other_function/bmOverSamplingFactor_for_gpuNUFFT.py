import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmOverSamplingFactor_for_gpuNUFFT(N_u, n_u):
    """Compute the oversampling factor for gpu_NUFFT.

    Parameters
    ----------
    N_u : array_like
        Upsampled dimensions.
    n_u : array_like
        Original dimensions.

    Returns
    -------
    float
        The computed oversampling factor.  A value of 1.0 indicates that th
the
        input arrays are already equal and no oversampling is required.

    Raises
    ------
    ValueError
        If the input arrays are empty, if the oversampling is not isotropic
isotropic,
        or if the dimensionality is greater than 3.
    """
    N_u = np.asarray(N_u).ravel()
    n_u = np.asarray(n_u).ravel()

    # Check for equal arrays (exact MATLAB isequal)
    if np.array_equal(N_u, n_u):
        return 1.0

    # Dimensionality check (MATLAB size(N_u(:),1))
    if N_u.size == 0 or n_u.size == 0:
        raise ValueError("Input arrays must not be empty")
    if N_u.size > 3:
        raise ValueError("Oversampling for gpu_NUFFT must be isotropic. ")

    # Compute oversampling factor element-wise
    myOsf = N_u / n_u
    if not np.allclose(myOsf, myOsf[0]):
        raise ValueError("Oversampling for gpu_NUFFT must be isotropic. ")

    return float(myOsf[0])
