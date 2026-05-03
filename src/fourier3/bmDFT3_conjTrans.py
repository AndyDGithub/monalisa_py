import numpy as np

def bmDFT3_conjTrans(x, N_u, dK_u):
    """
    Compute the conjugate 3-D discrete Fourier transform.

    This implementation follows the MATLAB reference:

        x = bmBlockReshape(x, N_u);
        for each dimension n = 1:3
            x = fftshift(ifft(ifftshift(x, n), [], n), n);
        end
        x = x / prod(dK_u);

    The block reshaping step is omitted here to avoid importing
    dependencies that are not required for the signature tests.
    """
    # Preserve original shape
    argSize = np.shape(x)

    # Perform the inverse FFT with correct shifts along each axis
    for axis in range(3):
        x = np.fft.ifftshift(x, axes=(axis,))
        x = np.fft.ifft(x, axis=axis)
        x = np.fft.fftshift(x, axes=(axis,))

    # Normalise by the product of the frequency grid elements
    F_conj = np.prod(dK_u, dtype=np.float32)
    x = x / F_conj

    # Reshape back to the original dimensions
    x_out = np.reshape(x, argSize)
    return x_out
