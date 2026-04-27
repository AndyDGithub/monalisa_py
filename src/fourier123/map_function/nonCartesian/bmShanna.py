from src.fourier123.map_function.nonCartesian.bmShanna_CUFFT_omp import bmShanna_CUFFT_omp
from src.fourier123.map_function.nonCartesian.bmShanna_FFTW_omp import bmShanna_FFTW_omp
from src.fourier123.map_function.nonCartesian.bmShanna_MATLAB import bmShanna_MATLAB
import numpy as np
from src.arrayUtility.arrayUtility import bmBlockReshape  # Import the missing arrayUtility module


def bmShanna(x, G, KFC, n_u, fft_lib_sFlag):
    """
    y = bmShanna(x, G, KFC, n_u, fft_lib_sFlag)

    This function computes the Fourier transform of CX -> F(CX) while
    gridding the points back to the trajectory. The Fourier transform is
    calculated using the FFT algorithm with different implementations.

    Authors:
        Bastien Milani
        CHUV and UNIL
        Lausanne - Switzerland
        May 2023

    Contributors:
        Dominik Helbing (Documentation & Comments)
        MattechLab 2024

    Parameters:
        x (array): The reconstructed image.
        G (bmSparseMat): The forward gridding matrix (grid -> trajectory).
        KFC (array): The kernel matrix used for deapodization multiplied with
            the fourier factor and the coil sensitivity.
        n_u (list): The size of the image space grid.
        fft_lib_sFlag (char): The FFT algorithm to be used. The options are
            'MATLAB' using the MATLAB intern FFT algorithm, 'FFTW' using the
            fastest Fourier transform in the west software library or 'CUFFT'
            using the CUDA fast Fourier transform library.

    Returns:
        y (array): The computed k-space data (FXC = y).

    Examples:
        y = bmShanna(x, Gu, KF, N_u, 'MATLAB')
    Use G.N_u if n_u is empty

    Raises:
        ValueError: If CUFFT or FFTW are used with N_u ~= n_u

    """
    # Ensure n_u is set properly
    if np.any(n_u == []):  # Equivalent to isempty in MATLAB
        n_u = G.N_u

    # Check and raise error for zero_filling not implemented with CUFFT or FFTW
    if (np.any(G.N_u != n_u) and fft_lib_sFlag == 'CUFFT') or \
       (np.any(G.N_u != n_u) and fft_lib_sFlag == 'FFTW'):
        raise ValueError('zero_filling is not implemented for Shanna_CUFFT/Shanna_FFTW.')

    # Call correct function based on the selected FFT library
    if fft_lib_sFlag == 'MATLAB':
        y = bmShanna_MATLAB(x, G, KFC, n_u)
    elif fft_lib_sFlag == 'FFTW':
        y = bmShanna_FFTW_omp(x, G, KFC)
    elif fft_lib_sFlag == 'CUFFT':
        y = bmShanna_CUFFT_omp(x, G, KFC)

    return y
