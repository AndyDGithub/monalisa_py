from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

from third_part.matlab_compat.matlab_native import single

def bmIDF2_conjTrans(x, N_u, dK_u):
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)
    n = 1
    x = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(x, n), [], n), n)
    n = 2
    x = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(x, n), [], n), n)
    F = single(np.prod(dK_u))
    x = x * F
    x_out = np.reshape(x, argSize)
    return x_out
