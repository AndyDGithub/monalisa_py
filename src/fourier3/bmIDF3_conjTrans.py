from src.arrayUtility.bmBlockReshape import bmBlockReshape
from third_part.matlab_compat.matlab_native import single
import numpy as np

def bmIDF3_conjTrans(x, N_u, dK_u):
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)
    n = 1
    x = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(x, n), [], n), n)
    n = 2
    x = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(x, n), [], n), n)
    n = 3
    x = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(x, n), [], n), n)
    F = single(np.prod(dK_u.ravel()))
    x = x * F
    x_out = np.reshape(x, argSize)
    return x_out
