from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.coilSense.map.bmCoilSense_pinv import bmCoilSense_pinv
from src.varargin.bmVarargin import bmVarargin
import numpy as np

def private_check(y, N_u):
    if y.dtype != np.single:
        raise ValueError('The data''y'' must be of class single')
    if y.shape[1] > y.shape[0]:
        raise ValueError('The data matrix ''y'' is probably not in the correct size')
    if np.sum(np.mod(N_u, 2)) > 0:
        raise ValueError('N_u must have all components even for the Fourier transform.')

def bmNasha_cartesian(y, N_u, dK_u, varargin):
    # argin_initial -----------------------------------------------------------
    C = bmVarargin(varargin)
    N_u = np.array(N_u).ravel().T
    imDim = len(N_u)
    F_inv = np.single(np.prod(N_u)*np.prod(dK_u))
    y = bmColReshape(y, N_u)
    nCh = y.shape[1]
    C_flag = False
    if not np.array_equiv(C, []):
        C_flag = True
        C = np.single(C)
    private_check(y, N_u)
    # END_argin_initial -------------------------------------------------------

    # fft
    x = np.reshape(y, [N_u, nCh])
    for n in range(1, 4):
        if imDim > (n-1):
            x = np.fft.ifftshift(x, axes=n)
            x = np.fft.ifft(x, axis=n)
            x = np.fft.fftshift(x, axes=n)
    x = np.reshape(x, [np.prod(N_u), nCh]) * F_inv

    # eventual coil_combine
    if C_flag:
        x = bmCoilSense_pinv(C, x, N_u)
    x = bmBlockReshape(x, N_u)

    return x
