"""Auto-generated from MATLAB source. Review manually before production use."""

import numpy as np
from scipy.sparse import csr_matrix

from src.fourier3.bcaNeith_interpolatekSpace3 import normalize

def KernelTypeExtraction(kspace, kernel):
    # Extract sizes
    Nx, Ny, Nz = kspace.shape

    # Get kernel dimensions
    Nxk = kernel[0]
    Nyk = kernel[1]
    Nzk = kernel[2]

    xstride = (Nxk - 1) / 2
    ystride = (Nyk - 1) / 2
    zstride = (Nzk - 1) / 2

    kern_types = []
    k = 1

    # Loop over the grid
    for i in range(Nx // 2 - xstride, Nx // 2 + xstride + 1):
        for j in range(1 + ystride, Ny - ystride):
            for iz in range(1 + zstride, Nz - zstride):
                kspace_kern = kspace[i-xstride:i+xstride+1, j-ystride:j+ystride+1, iz-zstride:iz+zstride+1]

                # Generate mask where kspace is nonzero
                kspace_kern_mask = np.abs(kspace_kern) > 0
                kspace_kern_mask = kspace_kern_mask.ravel()

                if np.linalg.norm(kspace_kern_mask) > 0:
                    # Normalize the mask
                    kspace_kern_mask = normalize(kspace_kern_mask, 'norm')
                else:
                    continue

                if k == 1:
                    kern_types.append(kspace_kern_mask)
                    k += 1
                else:
                    current_ker_types = np.array(kern_types).T
                    if not np.any(np.abs((current_ker_types * kspace_kern_mask - 1)) < 1e-9):
                        kern_types.append(kspace_kern_mask)
                        k += 1

    return csr_matrix(np.array(kern_types).T)


def bcaNeith_kernelTypeExtraction3(kspace, kernel):
    return KernelTypeExtraction(kspace, kernel)
