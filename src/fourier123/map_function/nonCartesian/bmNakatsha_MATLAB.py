from __future__ import annotations
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.image123.bmImCrope import bmImCrope
from src.sparseMat.m.bmSparseMat_vec import bmSparseMat_vec


def bmNakatsha_MATLAB(y, G, KFC_conj, C_flag, n_u):
    """Adjoint non-Cartesian Fourier transform using MATLAB-style iFFT (C*F*y).

    Authors:
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023

    Contributors:
    Dominik Helbing (Documentation & Comments)
    MattechLab 2024

    Parameters:
    y (array): k-space data, shape (nPt, nCh).
    G (bmSparseMat): Backward gridding sparse matrix (trajectory -> grid).
    KFC_conj (array): Deapodization kernel * conjugate Fourier factor * conjugate coil sensitivity.
    C_flag (bool): If True, sum over channels after deapodization.
    n_u (list or None): Image space grid size (uses G.N_u if None/empty).

    Returns:
    x (array): Image space data, shape (prod(n_u), nCh) or (prod(n_u), 1) if C_flag.
    """
    if C_flag is None:
        C_flag = False
    if n_u is None or (hasattr(n_u, '__len__') and len(np.atleast_1d(n_u)) == 0):
        n_u = G.N_u

    N_u = np.array(np.round(np.asarray(G.N_u).ravel()), dtype=np.int32).astype(float)
    n_u = np.array(np.round(np.asarray(n_u).ravel()),   dtype=np.int32).astype(float)
    N_u_int = N_u.astype(int).tolist()
    n_u_int = n_u.astype(int).tolist()

    imDim = len(N_u_int)

    # Sparse matrix multiplication: G' * y  (adjoint gridding, trajectory -> uniform grid)
    x = bmSparseMat_vec(G, y, 'omp', 'complex', False)  # (prod(N_u), nCh)

    # Reshape to block format (...N_u..., nCh)
    x = bmBlockReshape(x, N_u_int)

    # Inverse FFT per spatial dimension (fftshift(ifft(ifftshift(x, n), [], n), n))
    for dim in range(imDim):
        x = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(x, axes=dim), axis=dim), axes=dim)

    # Back to column format (prod(N_u), nCh)
    x = bmColReshape(x, N_u_int)

    # Crop if the oversampled grid N_u differs from the target image grid n_u
    if not np.array_equal(N_u_int, n_u_int):
        x = bmBlockReshape(x, N_u_int)
        x = bmImCrope(x, N_u_int, n_u_int)
        x = bmColReshape(x, n_u_int)

    # Deapodization (and optional coil sensitivity weighting)
    x = x * KFC_conj  # (prod(n_u), nCh)

    # Sum over coil channels if C_flag is set
    if C_flag:
        x = np.sum(x, axis=1, keepdims=True)  # (prod(n_u), 1)

    return x
