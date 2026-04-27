from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

def bmDFT1_conjTrans(x, N_u, dK_u):
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)
    n = 1
    x = np.fft.ifftshift(np.fft.ifft(np.fft.fftshift(x, n), axes=[n]), axes=[n]) * (1 / np.prod(dK_u))
    x_out = np.reshape(x, argSize)
    return x_out
