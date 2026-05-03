"""
bmNasha - non-Cartesian → image-space reconstruction via sparse gridding.

Port of MATLAB bmNasha.m. Uses bmSparseMatScipy from bmTraj2SparseMat.
"""

import numpy as np

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.fourier3.bmIDF3 import bmIDF3
from src.fourier123.prep_function.bmK import bmK


def bmNasha(y, G, N_u, C=None, K=None, fft_lib_flag=None):
    """
    Grid non-Cartesian data to a uniform grid and transform to image space.

    Parameters
    ----------
    y : array (nPt,) or (nPt, nCh)
        Non-Cartesian k-space data.
    G : bmSparseMatScipy
        Gridding matrix (Gn), shape [Nu_tot, nPt].
    N_u : array-like [Nx, Ny, Nz]
        Reconstruction grid size.  If None uses G.N_u.
    C : array or None
        Coil sensitivities in block format. If given, coil-combine output.
    K : array or None
        Pre-computed deapodization kernel (Nu_tot, nCh). Computed if None.
    fft_lib_flag : str or None
        Ignored (always uses numpy FFT).

    Returns
    -------
    x : ndarray, complex64, shape (Nx, Ny, Nz, nCh) or (Nx, Ny, Nz)
        Image in block format.
    """
    G_N_u = np.asarray(G.N_u).ravel().astype(int)
    if N_u is None or (hasattr(N_u, '__len__') and len(np.asarray(N_u).ravel()) == 0):
        N_u_arr = G_N_u
    else:
        N_u_arr = np.asarray(N_u).ravel().astype(int)

    dK_u = np.asarray(G.d_u).ravel()
    kernelType = G.kernel_type
    nWin = G.nWin
    kernelParam = G.kernelParam

    y = np.asarray(y, dtype=np.complex64)
    if y.ndim == 1:
        y = y[:, np.newaxis]
    nPt, nCh = y.shape

    # ── sparse gridding: G.matrix @ y → (Nu_tot, nCh) ──────────────────────
    x = G.matrix @ y               # scipy handles complex single
    if not np.iscomplexobj(x):
        x = x.astype(np.complex64)
    else:
        x = np.asarray(x, dtype=np.complex64)

    Nu_tot = int(np.prod(G_N_u))
    Nx, Ny, Nz = int(G_N_u[0]), int(G_N_u[1]), int(G_N_u[2])

    # Reshape (Nu_tot, nCh) to (Nx, Ny, Nz, nCh) using F-order (matches gridder indexing)
    x = x.reshape((Nx, Ny, Nz, nCh), order='F')

    # ── inverse Fourier transform ────────────────────────────────────────────
    x = bmIDF3(x, G_N_u, dK_u)    # returns (Nx, Ny, Nz, nCh)

    # ── deapodization kernel ─────────────────────────────────────────────────
    if K is None:
        K_flat = bmK(G_N_u, dK_u, nCh, kernelType, nWin, kernelParam)
    else:
        K_flat = np.asarray(K)

    # K_flat: (Nu_tot, nCh) with C-order spatial indexing → reshape C-order
    K_block = K_flat.reshape((Nx, Ny, Nz, nCh))   # C-order (bmBlockReshape convention)
    x = x * K_block

    # ── optional crop (N_u < G_N_u) ─────────────────────────────────────────
    if not np.array_equal(N_u_arr, G_N_u):
        from src.image123.bmImCrope import bmImCrope
        x = bmImCrope(x, G_N_u, N_u_arr)

    # ── optional coil combination ────────────────────────────────────────────
    if C is not None:
        from src.coilSense.map.bmCoilSense_pinv import bmCoilSense_pinv
        x = bmCoilSense_pinv(C, x, N_u_arr)

    return x
