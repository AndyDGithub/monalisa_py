from src.arrayUtility.bmBlockReshape import bmBlockReshape
from third_part.matlab_compat.matlab_native import single
import numpy as np

def bmDFT2_conjTrans(x, N_u, dK_u):
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)
    n = 1
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, n), [], n), n)
    n = 2
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, n), [], n), n)
    F_conj = single(1/np.prod(single(dK_u.ravel())))
    x = x * F_conj
    x_out = np.reshape(x, argSize)
    return x_out
