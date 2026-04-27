import numpy as np

from src.sparseMat.m.bmSparseMat_vec import ndims

def bmIDF(k, nDim=1, NZero=0, gridType=None):
    # ... (adapt the MATLAB code to Python)

    if gridType is None:
        # Automatically determine gridType based on k and N
        pass

    # Zero-padding
    if NZero > 0:
        f = np.pad(f, ((NZero//2, NZero-NZero//2),) * ndims(f))

    # Apply IFFT based on gridType
    if gridType == 0 or gridType == 2:
        iFf = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(f, axes=nDim), 
axis=nDim) * N * dK, axes=nDim)

    # ... (adapt the rest of the gridType conditions)

    return iFf, outGridType
