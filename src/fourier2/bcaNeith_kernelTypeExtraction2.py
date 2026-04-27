"""Auto-generated from MATLAB source. Review manually before production use."""

import numpy as np
from scipy import signal

def bcaNeith_kernelTypeExtraction(kspace, kernel):
    Nx, Ny = kspace.shape[:2]  # Extract data size

    Nxk = kernel[0]  # Extract kernel sizes
    Nyk = kernel[1]

    xstride = (Nxk - 1) / 2  # Setting the properties of how kernel is convolved
    ystride = (Nyk - 1) / 2

    kern_types = []  # Initialize the kernel types data structure
    k = 1  # Counter for types

    for i in range(xstride + 1, Nx - xstride):
        for j in range(ystride + 1, Ny - ystride):
            if np.abs(kspace[i, j]) == 0:  # If data is missing, try to find the kernel type
                kspace_kern = kspace[i-xstride:i+xstride+1, j-ystride:j+ystride+1]
                kspace_kern_mask = (np.abs(kspace_kern) > 0).ravel()

                if np.linalg.norm(kspace_kern_mask) > 0:
                    kspace_kern_mask /= np.linalg.norm(kspace_kern_mask)

                    if len(kern_types) == 0:
                        kern_types = np.column_stack((kern_types, kspace_kern_mask))
                        k += 1
                    else:
                        if np.isclose(np.sum(np.abs(np.dot(kern_types, kspace_kern_mask) - 1)), 0):
                            continue
                        else:
                            kern_types = np.column_stack((kern_types, kspace_kern_mask))
                            k += 1

    return kern_types


def bcaNeith_kernelTypeExtraction2(kspace, kernel):
    return bcaNeith_kernelTypeExtraction(kspace, kernel)
