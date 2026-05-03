# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np


def bmDFT2_conjTrans(x, N_u, dK_u):
    """
    Compute the 2D DFT conjugate transform of a given input array.

    Parameters
    ----------
    x : np.ndarray
        Input array.
    N_u : tuple or list
        Number of elements in each dimension.
    dK_u : np.ndarray
        Array containing the spacing between elements in each dimension.

    Returns
    -------
    np.ndarray
        The 2D DFT conjugate transform of the input array.
    """
    argSize = x.shape
    x = bmBlockReshape(x, N_u)

    # First axis (0-based indexing)
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, axes=0), axis=0), 
axes=0)

    # Second axis
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, axes=1), axis=1), 
axes=1)

    # Conjugate scaling factor
    F_conj = np.float32(1.0 / np.prod(dK_u.ravel(), dtype=np.float32))
    x = x * F_conj

    x_out = np.reshape(x, argSize)
    return x_out
