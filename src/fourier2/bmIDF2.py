from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

def bmIDF2(x, N_u, dK_u):
    argSize = np.shape(x)
    x = bmBlockReshape(x, N_u)
    n = 1
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, n), [], n), n) * (2 ** n)
    n = 2
    x = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(x, n), [], n), n) * (2 ** n)
    F = np.prod(N_u.ravel()) * np.prod(dK_u.ravel())
    x *= F
    iFx = np.reshape(x, argSize)
    return iFx
