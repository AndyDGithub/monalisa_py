import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape

def bmIDF3(x, N_u, dK_u):
    """
    iFx = bmDFT3(x, N_u, dK_u)

    This function computes the inverse discrete Fourier transform for three
three-dimensional data using a fast Fourier transform (FFT) algorithm.

    Authors:
      Bastien Milani
      CHUV and UNIL
      Lausanne - Switzerland
      May 2023

    Parameters:
      x (3D array): Contains the data on which the iFFT should be performed
performed. The zero-frequency component is assumed to be in the center of x
x.
      N_u (list): Contains the size of the grid.
      dK_u (list): Contains the distances between grid points in every dime
dimension.

    Returns:
      iFx (array): Contains the transformed data, having the same size as x
x. The zero-frequency component is given in the center of iFx.
    """
    N_u = np.array(N_u).ravel().astype(int)
    dK_u = np.array(dK_u).ravel().astype(np.float64)

    argSize = x.shape
    x = bmBlockReshape(x, N_u)  # → (Nx, Ny, Nz, nCh)

    # Apply centered iFFT along each spatial dimension (axes 0, 1, 2)
    for ax in range(3):
        x = np.fft.ifftshift(
            np.fft.ifft(np.fft.ifftshift(x, axes=ax), axis=ax),
            axes=ax
        )

    # Fourier scaling: prod(N_u) * prod(dK_u)  - matches MATLAB convention
    F = np.float32(np.prod(N_u) * np.prod(dK_u))
    x = x * F

    return x.reshape(argSize)
