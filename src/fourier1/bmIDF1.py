from src.arrayUtility.bmBlockReshape import bmBlockReshape  # IMPORT THIS FUNCTION
import numpy as np


def bmIDF1(x, N_u, dK_u):
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)
    n = 1
    x = np.fft.ifftshift(np.fft.ifft2(np.fft.ifftshift(x, n)), axes=n) * np.prod(N_u) * np.prod(dK_u)
    iFx = np.reshape(x, argSize)
    return iFx
