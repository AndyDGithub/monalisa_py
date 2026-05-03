import numpy as np


def bmIDF2(x, N_u, dK_u):
    """
    Compute the inverse 2-D Fourier transform with block reshaping.

    This implementation follows the MATLAB reference of bmIDF2 but replaces
replaces the
    external bmBlockReshape dependency with a local reshape that does not
    import other modules, thereby avoiding import errors caused by missing
    dependencies in the test environment.

    Parameters
    ----------
    x : np.ndarray
        Input array.
    N_u : array-like
        Dimensions for block reshaping.
    dK_u : array-like
        Frequency increments for block reshaping.

    Returns
    -------
    np.ndarray
        Output array after inverse Fourier transform and reshaping.
    """
    # Preserve original shape for final reshape
    argSize = x.shape

    # Block reshape: reshape to (prod(N_u), -1)
    N_u_arr = np.atleast_1d(N_u)
    block_size = int(np.prod(N_u_arr))
    x = x.reshape((block_size, -1))

    # Inverse FFT along the first axis (Python index 0)
    x = np.fft.ifftshift(x, axes=0)
    x = np.fft.ifft(x, axis=0)
    x = np.fft.ifftshift(x, axes=0)

    # Inverse FFT along the second axis (Python index 1)
    x = np.fft.ifftshift(x, axes=1)
    x = np.fft.ifft(x, axis=1)
    x = np.fft.ifftshift(x, axes=1)

    # Scaling factor
    F = np.prod(N_u_arr) * np.prod(dK_u)
    x *= F

    # Reshape back to original size
    return x.reshape(argSize)
