from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np
from third_part.matlab_compat.matlab_native import single

def bmDFT3_conjTrans(x, N_u, dK_u):
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)
    n = 1
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, n), [], n), n)
    n = 2
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, n), [], n), n)
    n = 3
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, n), [], n), n)
    F_conj = single(prod(single(dK_u.ravel())))
    x = x / F_conj
    x_out = np.reshape(x, argSize)
    return x_out
