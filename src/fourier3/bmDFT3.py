import numpy as np

def bmDFT3(x, N_u, dK_u):
    """
    3-D discrete Fourier transform (centered).

    Parameters
    ----------
    x : ndarray
        Input array.  It may contain multiple blocks; the function reshapes
reshapes it
        into blocks of size ``N_u`` before performing the transform.
    N_u : array-like
        List or array of dimensions ``[Nx, Ny, Nz]`` of each block.
    dK_u : array-like
        Spacing between grid points in each dimension ``[dKx, dKy, dKz]``.

    Returns
    -------
    Fx : ndarray
        Fourier-transformed array with the same shape as the input ``x``.
    """
    N_u = np.asarray(N_u, dtype=int).ravel()
    dK_u = np.asarray(dK_u, dtype=float).ravel()

    # Preserve original shape for reshaping back later
    argSize = x.shape

    # Reshape x into blocks of size N_u (if necessary)
    if x.size == np.prod(N_u):
        x = x.reshape(N_u)
    elif x.size % np.prod(N_u) == 0:
        # Assume trailing dimensions are channel dimension
        block_shape = tuple(N_u) + x.shape[len(N_u):]
        x = x.reshape(block_shape)

    # Apply centered FFT along each of the first three axes
    for ax in range(3):
        x = np.fft.fftshift(
            np.fft.fft(np.fft.ifftshift(x, axes=ax), axis=ax),
            axes=ax
        )

    # Normalisation factor (product of block size and grid spacings)
    F = np.prod(N_u) * np.prod(dK_u)

    # Scale the result
    x = x / F

    # Reshape back to the original input shape
    return x.reshape(argSize)
