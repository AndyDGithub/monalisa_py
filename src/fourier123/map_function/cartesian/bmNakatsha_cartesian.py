from src.varargin.bmVarargin import bmVarargin
import numpy as np

def bmNakatsha_cartesian(y, N_u, dK_u, varargin):
    # argin_initial -----------------------------------------------------------
    N_u = np.array(N_u).ravel().T
    imDim = np.shape(N_u)[0]
    nCh = np.shape(y)[1]
    F_conj = 1 / np.prod(dK_u) ** 2
    C_conj = bmVarargin(varargin)
    C_flag = False
    if not C_conj.empty:
        C_flag = True
        C = C_conj
    private_check(y, N_u)
    # END_argin_initial -------------------------------------------------------

    # fft
    x = np.reshape(y, [N_u, nCh])
    for n in range(1, 4):  # TODO: Replace this loop with numpy's more efficient approach if possible
        if imDim > (n - 1):
            x = np.fft.ifftshift(x, axes=n)
            x = np.fft.ifft(x, axis=n)
            x = np.fft.fftshift(x, axes=n)
    x = np.reshape(x, [np.prod(N_u), nCh])
    x = x * F_conj

    # coil combine
    if C_flag:
        x = np.sum(C_conj * x, axis=1)

    return x

def private_check(y, N_u):
    if y.dtype != np.single:
        raise ValueError("The data 'y' must be of type single")
    if y.shape[0] > y.shape[1]:
        raise ValueError("The data matrix 'y' is probably not in the correct size")
    if np.mod(N_u, 2).sum() > 0:
        raise ValueError("N_u must have all components even for the Fourier transform.")
