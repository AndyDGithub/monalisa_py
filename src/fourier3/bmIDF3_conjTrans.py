# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

"""
function x_out = bmIDF3_conjTrans(x, N_u, dK_u)

This function performs the conjugate Fourier transform of the input array `
`x`
by reshaping it according to `N_u`, applying a 3-D FFT with centering
(`fftshift/ifftshift`) on each axis, scaling by the product of `dK_u`,
and finally reshaping back to the original size.

Parameters
----------
x : numpy.ndarray
    Input data array.
N_u : tuple or list
    Target shape for reshaping `x` before the FFT.
dK_u : tuple or list
    Frequency scaling factors; the product is used as a scalar multiplier.

Returns
-------
numpy.ndarray
    Transformed array with the same shape as the original input.
"""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

def bmIDF3_conjTrans(x, N_u, dK_u):
    """
    Compute the conjugate transform of a signal using FFTs.

    Parameters
    ----------
    x : np.ndarray
        Input signal.
    N_u : tuple
        Dimensions for reshaping.
    dK_u : tuple
        Frequencies for scaling.

    Returns
    -------
    np.ndarray
        Transformed signal.
    """
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)

    # Perform FFT along each axis with centering
    for axis in (1, 2, 3):
        x = np.fft.fftshift(
            np.fft.fft(
                np.fft.ifftshift(x, axes=axis),
                axis=axis
            ),
            axes=axis
        )

    F = np.prod(dK_u)
    x = x * F

    x_out = np.reshape(x, argSize)
    return x_out
