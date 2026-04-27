import numpy as np
from scipy.ndimage import convolve

def bmConv3(f, h, dx, dy, dz):
    Nx = f.shape[0]
    Ny = f.shape[1]
    Nz = f.shape[2]

    dR = dx * dy * dz

    # Calculate the convolution using SciPy's convolve function
    s = convolve(f, h, mode='constant', cval=0) / (dx * dy * dz)

    return s
