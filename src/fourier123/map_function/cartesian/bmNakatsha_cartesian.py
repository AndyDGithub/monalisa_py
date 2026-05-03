from __future__ import annotations
import numpy as np
from src.varargin.bmVarargin import bmVarargin


def bmNakatsha_cartesian(y, N_u, dK_u, varargin=None):
    """Inverse FFT gridding for Cartesian data with optional coil combination.

    Parameters:
    y (array): Input k-space data of shape (nPt, nCh) or (nPt,).
    N_u (array-like): Grid sizes, one per dimension.
    dK_u (array-like): K-space step sizes per dimension.
    varargin: Optional coil sensitivity array C_conj for coil combination.

    Returns:
    x (array): Reconstructed image in column format (nPt, nCh) or (nPt, 1)
               after coil combination.
    """
    # Initialise arguments
    N_u  = np.asarray(N_u).ravel().astype(int)
    dK_u = np.asarray(dK_u).ravel().astype(float)
    imDim = len(N_u)
    nCh   = int(y.shape[1]) if y.ndim > 1 else 1
    F_conj = 1.0 / np.prod(dK_u) ** 2

    C_conj = bmVarargin(varargin) if varargin else None
    C_flag = C_conj is not None and np.asarray(C_conj).size > 0

    _private_check(y, N_u)

    # Inverse FFT along each spatial dimension
    x = np.reshape(y, list(N_u) + [nCh])
    for n in range(imDim):
        x = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(x, axes=n), axis=n), axes=n)
    x = np.reshape(x, [int(np.prod(N_u)), nCh])
    x = x * F_conj

    # Optional coil combination
    if C_flag:
        C = np.asarray(C_conj)
        x = np.sum(C * x, axis=1, keepdims=True)

    return x


def _private_check(y, N_u):
    """Validate input data array."""
    if not np.issubdtype(y.dtype, np.floating) and not np.issubdtype(y.dtype, np.complexfloating):
        raise ValueError("The data 'y' must be numeric (floating or complex)")
    if y.ndim > 1 and y.shape[0] > y.shape[1]:
        raise ValueError("The data matrix 'y' is probably not in the correct size")
    if np.mod(N_u, 2).sum() > 0:
        raise ValueError("N_u must have all components even for the Fourier transform.")
