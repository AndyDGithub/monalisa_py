from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.gridding123.m.bmGut_partialCartesian import bmGut_partialCartesian
from src.image123.bmImCrope import bmImCrope
import numpy as np

def private_check(y, FC_conj, N_u, n_u, nPt, nCh, C_flag):
    """
    Validate input data and parameters according to MATLAB's private_check function.
    """
    if not isinstance(y, np.ndarray) or y.dtype != np.float32:
        raise ValueError("The data 'y' must be of class single (np.float32).")

    if not isinstance(FC_conj, np.ndarray) or FC_conj.dtype != np.float32:
        raise ValueError("The matrix 'FC_conj' must be of class single (np.float32).")

    if y.shape != (nPt, nCh):
        raise ValueError("The data matrix 'y' is not in the correct size.")

    if C_flag and FC_conj.shape != (int(np.prod(N_u)), nCh):
        raise ValueError("The matrix 'C' is not in the correct size.")

    if np.mod(N_u, 2).sum() > 0:
        raise ValueError("N_u must have all components even for the Fourier transform.")

    if np.mod(n_u, 2).sum() > 0:
        raise ValueError("n_u must have all components even for the Fourier transform.")

def bmNakatsha_partialCartesian(y, ind_u, FC_conj, N_u, n_u, dK_u):
    """Auto-generated from MATLAB source. Review manually before production use."""

    # argin_initial -----------------------------------------------------------
    C_flag = False
    if FC_conj is None or np.prod(dK_u) == 0:
        FC_conj = 1 / np.prod(np.array(dK_u, dtype=np.float32))
        C_flag = False
    else:
        C_flag = True

    if n_u is None:
        n_u = N_u
    n_u = np.array(n_u, dtype=np.int32)
    N_u = np.array(N_u, dtype=np.int32)
    nPt = y.shape[0]
    nCh = y.shape[1]
    imDim = N_u.size

    private_check(y, FC_conj, N_u, n_u, nPt, nCh, C_flag)
    # END_argin_initial -------------------------------------------------------

    # gridding
    x = bmGut_partialCartesian(y, ind_u, N_u)

    # fft
    x = bmBlockReshape(x, N_u)
    for n in range(1, 4):
        if imDim > (n - 1):
            x = np.fft.ifftshift(np.fft.ifft2(np.fft.fftshift(x, axes=(n - 1)), axes=n), axes=(n - 1))

    x = bmColReshape(x, N_u)

    # eventual crope
    if not np.array_equal(N_u, n_u):
        x = bmBlockReshape(x, N_u)
        x = bmImCrope(x, N_u, n_u)
        x = bmColReshape(x, n_u)

    # Fourier_factor and coil_combine
    x *= FC_conj

    if C_flag:
        x = np.sum(x, axis=2)

    return x
