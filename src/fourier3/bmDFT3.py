import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape


def bmDFT3(x, N_u, dK_u):
    """
    3-D discrete Fourier transform (centered).

    Port of MATLAB bmDFT3.m.  Zero-frequency component is assumed to be
    at the centre of x; it is returned to the centre after the FFT.

    Parameters
    ----------
    x    : ndarray, shape (..., Nx, Ny, Nz, nCh) or similar block layout
    N_u  : array-like, [Nx, Ny, Nz]
    dK_u : array-like, [dKx, dKy, dKz]

    Returns
    -------
    Fx   : ndarray, same shape as input
    """
    N_u  = np.array(N_u).ravel().astype(int)
    dK_u = np.array(dK_u).ravel().astype(np.float64)

    argSize = x.shape
    x = bmBlockReshape(x, N_u)   # → (Nx, Ny, Nz, nCh)

    for ax in range(3):
        x = np.fft.fftshift(
                np.fft.fft(np.fft.ifftshift(x, axes=ax), axis=ax),
                axes=ax)

    F = np.prod(N_u) * np.prod(dK_u)
    x = x / F

    return x.reshape(argSize)
