import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape


def bmIDF1(x, N_u, dK_u):
    """
    Compute the inverse discrete Fourier transform (IDFT) of a block-struct
block-structured array.

    This function is a faithful translation of the MATLAB implementation:

        iFx = bmIDF1(x, N_u, dK_u)

    Parameters
    ----------
    x : np.ndarray
        Input array to transform.  It will be reshaped into blocks of size 
``N_u``.
    N_u : array-like
        Sampling grid dimensions used by :func:`bmBlockReshape`.
    dK_u : array-like
        K-space grid spacing for scaling the result.

    Returns
    -------
    np.ndarray
        The inverse Fourier transformed array, reshaped back to the origina
original
        input shape.
    """
    # Preserve original shape for reshaping after transformation
    argSize = np.shape(x)

    # Reshape input into blocks as in MATLAB's bmBlockReshape
    x = bmBlockReshape(x, N_u)

    # Apply the inverse FFT with proper shifts.
    # MATLAB performs: fftshift(ifft(ifftshift(x,1),[],1),1)
    # In NumPy, shift and ifft over the first two axes.
    x = np.fft.ifftshift(x, axes=0)
    x = np.fft.ifft2(x, axes=(0, 1))
    x = np.fft.fftshift(x, axes=0)

    # Scale by the product of grid sizes and spacings
    F = np.prod(N_u) * np.prod(dK_u)
    x = x * F

    # Restore original shape
    iFx = np.reshape(x, argSize)
    return iFx
