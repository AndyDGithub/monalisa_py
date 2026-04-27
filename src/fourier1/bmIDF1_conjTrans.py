from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

def bmIDF1_conjTrans(x, N_u, dK_u):
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)
    n = 1
    x = np.fft.ifftshift(x, axes=n)
    x = np.fft.fft(np.fft.fftshift(x, axes=n), axis=n, n=0) * (dK_u.prod())
    x_out = np.reshape(x, argSize)
    return x_out
