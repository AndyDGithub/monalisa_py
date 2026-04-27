import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape


def bmIDF3(x, N_u, dK_u):
    """
    3-D inverse discrete Fourier transform (centered).

    Port of MATLAB bmIDF3.m. Assumes the zero-frequency component is at
    the centre of x. After the iFFT the zero-frequency is returned to
    the centre.

    Parameters
    ----------
    x    : ndarray, shape (..., Nx, Ny, Nz, nCh) or similar block layout
    N_u  : array-like, [Nx, Ny, Nz]
    dK_u : array-like, [dKx, dKy, dKz]

    Returns
    -------
    iFx  : ndarray, same shape as input
    """
    N_u  = np.array(N_u).ravel().astype(int)
    dK_u = np.array(dK_u).ravel().astype(np.float64)

    argSize = x.shape
    x = bmBlockReshape(x, N_u)   # → (Nx, Ny, Nz, nCh)

    # Apply centered iFFT along each spatial dimension (axes 0, 1, 2)
    for ax in range(3):
        x = np.fft.fftshift(
                np.fft.ifft(np.fft.ifftshift(x, axes=ax), axis=ax),
                axes=ax)

    # Fourier scaling: prod(N_u) * prod(dK_u)  — matches MATLAB convention
    F = np.float32(np.prod(N_u) * np.prod(dK_u))
    x = x * F

    return x.reshape(argSize)
