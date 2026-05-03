from __future__ import annotations
import numpy as np
from src.fourier123.map_function.nonCartesian.bmNakatsha_MATLAB import bmNakatsha_MATLAB


def bmNakatsha(y, G, KFC_conj, C_flag, n_u, fft_lib_sFlag):
    """Dispatcher for the adjoint non-Cartesian Fourier transform (C*F*y).

    Authors:
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023

    Contributors:
    Dominik Helbing (Documentation & Comments)
    MattechLab 2024

    Parameters:
    y (array): The data in k-space to be gridded and transformed into image space.
    G (bmSparseMat): The backward gridding sparse matrix.
    KFC_conj (array): Deapodization kernel * conjugate Fourier factor * conjugate coil sensitivity.
    C_flag (bool): If True, KFC_conj contains the conjugate of C and channels are summed.
    n_u (list or None): Size of the image space grid (uses G.N_u if None/empty).
    fft_lib_sFlag (str): FFT implementation: 'MATLAB', 'FFTW', or 'CUFFT'.

    Returns:
    x (array): Image space data (C*F*y).
    """
    if n_u is None or (hasattr(n_u, '__len__') and len(np.atleast_1d(n_u)) == 0):
        n_u = G.N_u

    if not C_flag and fft_lib_sFlag in ('FFTW', 'CUFFT'):
        raise ValueError("'C_flag' must be 'true' for the FFTW/CUFFT version of bmNakatsha.")

    n_u_arr = np.asarray(n_u).ravel()
    G_N_u = np.asarray(G.N_u).ravel()
    if not np.array_equal(G_N_u, n_u_arr) and fft_lib_sFlag in ('CUFFT', 'FFTW'):
        raise ValueError('zero_filling is not implemented for Shanna_CUFFT/FFTW.')

    if fft_lib_sFlag == 'MATLAB':
        return bmNakatsha_MATLAB(y, G, KFC_conj, C_flag, n_u)
    elif fft_lib_sFlag == 'FFTW':
        raise NotImplementedError('bmNakatsha_FFTW_omp is not implemented in the Python port.')
    elif fft_lib_sFlag == 'CUFFT':
        raise NotImplementedError('bmNakatsha_CUFFT_omp is not implemented in the Python port.')
    else:
        raise ValueError(f"Unknown fft_lib_sFlag: {fft_lib_sFlag!r}")
