from __future__ import annotations
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.image123.bmImZeroFill import bmImZeroFill
from src.sparseMat.m.bmSparseMat_vec import bmSparseMat_vec


def bmShanna_MATLAB(x, G, KFC, n_u):
    """Forward non-Cartesian Fourier transform using MATLAB-style FFT (F(C*x)).

    Authors:
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023

    Contributors:
    Dominik Helbing (Documentation & Comments)
    MattechLab 2024

    Parameters:
    x (array): Image space data, shape (prod(n_u), 1) or (prod(n_u), nCh).
    G (bmSparseMat): Forward gridding sparse matrix (grid -> trajectory).
    KFC (array): Deapodization kernel * Fourier factor * coil sensitivity, shape (prod(n_u), nCh).
    n_u (list or None): Image space grid size (uses G.N_u if None/empty).

    Returns:
    y (array): k-space data at non-Cartesian trajectory points, shape (nPt, nCh).
    """
    if n_u is None or (hasattr(n_u, '__len__') and len(np.atleast_1d(n_u)) == 0):
        n_u = G.N_u

    N_u = np.array(np.round(np.asarray(G.N_u).ravel()), dtype=np.int32).astype(float)
    n_u = np.array(np.round(np.asarray(n_u).ravel()),   dtype=np.int32).astype(float)
    N_u_int = N_u.astype(int).tolist()
    n_u_int = n_u.astype(int).tolist()

    imDim = len(N_u_int)

    x_arr = np.asarray(x)
    x_size_2 = x_arr.shape[1] if x_arr.ndim > 1 else 1
    KFC_arr = np.asarray(KFC)

    # Determine number of channels
    if x_size_2 == 1:
        nCh = KFC_arr.shape[1] if KFC_arr.ndim > 1 else 1
    else:
        nCh = x_size_2

    # Replicate single image across all channels if needed
    if x_size_2 < nCh:
        x_arr = np.tile(x_arr, (1, nCh))

    # Deapodization + coil sensitivity weighting
    x_arr = x_arr * KFC_arr  # (prod(n_u), nCh)

    # Zero-pad to oversampled grid if N_u > n_u
    if not np.array_equal(N_u_int, n_u_int):
        x_arr = bmBlockReshape(x_arr, n_u_int)
        x_arr = bmImZeroFill(x_arr, N_u_int, n_u_int, 'complex_single')
        x_arr = bmColReshape(x_arr, N_u_int)

    # Reshape to block format for FFT (...N_u..., nCh)
    x_arr = bmBlockReshape(x_arr, N_u_int)

    # Forward FFT per spatial dimension (fftshift(fft(ifftshift(x, n), [], n), n))
    for dim in range(imDim):
        x_arr = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(x_arr, axes=dim), axis=dim), axes=dim)

    # Back to column format (prod(N_u), nCh)
    x_arr = bmColReshape(x_arr, N_u_int)

    # Forward gridding sparse mat multiply (grid -> trajectory)
    y = bmSparseMat_vec(G, x_arr, 'omp', 'complex', False)

    return y
