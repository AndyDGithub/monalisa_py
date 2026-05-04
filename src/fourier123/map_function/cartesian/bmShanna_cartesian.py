import numpy as np
from src.varargin.bmVarargin import bmVarargin
from src.arrayUtility.bmColReshape import bmColReshape

from src.fourier123.map_function.cartesian.bmNasha_cartesian import private_check
def bmShanna_cartesian(x: np.ndarray, N_u, dK_u, *varargin) -> np.ndarray:
    """
    Cartesian Fourier transform with optional coil decomposition.

    Parameters
    ----------
    x : np.ndarray
        Input data array.
    N_u : array-like
        Array of dimensions for reshaping.
    dK_u : array-like
        Array used for scaling factor.
    *varargin : list
        Optional arguments for coil decomposition.

    Returns
    -------
    np.ndarray
        Processed data array.
    """
    # Ensure x is float32 as MATLAB expects single precision
    x = x.astype(np.float32, copy=False)

    # Reshape input
    x = bmColReshape(x, N_u)

    # Convert N_u and dK_u to numpy arrays
    N_u_arr = np.asarray(N_u, dtype=np.float32).flatten()
    dK_u_arr = np.asarray(dK_u, dtype=np.float32).flatten()
    im_dim = N_u_arr.size
    n_ch = x.shape[1]

    # Scaling factor
    F = 1.0 / (np.prod(N_u_arr) * np.prod(dK_u_arr))
    F = np.float32(F)

    # Optional coil decomposition
    C = bmVarargin(*varargin)
    C_flag = bool(C)
    if C_flag:
        C_arr = np.asarray(C, dtype=np.float32)
        # Broadcast multiplication
        x = x * C_arr

    # Validation
    private_check(x, N_u_arr)

    # FFT processing
    y = x.reshape((*N_u_arr.astype(int), n_ch))
    for n in range(3):
        if im_dim > n:
            y = np.fft.ifftshift(y, axes=(n,))
            y = np.fft.fft(y, axis=n)
            y = np.fft.fftshift(y, axes=(n,))
    y = y.reshape((int(np.prod(N_u_arr)), n_ch))

    return (y.astype(np.float32) * F).copy()
