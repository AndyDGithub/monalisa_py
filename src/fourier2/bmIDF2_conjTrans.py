from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np
from third_part.matlab_compat.matlab_native import single

def bmIDF2_conjTrans(x, N_u, dK_u):
    """Conjugate transpose of the input array `x`.

    Parameters
    ----------
    x : ndarray
        Input array.
    N_u : array_like
        Unpacking specification for :func:`bmBlockReshape`.
    dK_u : array_like
        Sampling spacing vector used for scaling.

    Returns
    -------
    ndarray
        The conjugate-transposed array with the same shape as the original 
input.
    """
    original_shape = np.shape(x)
    x = bmBlockReshape(x, N_u)

    # First Fourier transform along axis 1
    n = 1
    x = np.fft.ifftshift(x, axes=n)
    x = np.fft.fft(x, axis=n)
    x = np.fft.fftshift(x, axes=n)

    # Second Fourier transform along axis 2
    n = 2
    x = np.fft.ifftshift(x, axes=n)
    x = np.fft.fft(x, axis=n)
    x = np.fft.fftshift(x, axes=n)

    scaling_factor = single(np.prod(dK_u))
    x = x * scaling_factor

    return np.reshape(x, original_shape)
