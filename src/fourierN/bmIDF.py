import numpy as np

from src.sparseMat.m.bmSparseMat_vec import ndims
from src.geom123 import bmTraj  # Added import for bmTraj

def bmIDF(k, nDim=1, NZero=0, gridType=None):
    """
    Compute the inverse discret Fourier transform 'iFf' of an input vector 


'f' with grid 'k' or grid-step dK.
    The ifft function of MATLAB is used.

    f can be an array of any size.
    k must be a column or line array, and its length must be size(f, nDim).
nDim).
nDim).
nDim).
    Or it can be a scalar, which is then interpreted as dK.

    nZero = NZero is the number of zeros to add as zero-pading. Default val
value is nZero = 0; Default value is used if empty.
    nDim = nDim is the dimension in which the Fourier transform is done. Th
The default value is the first non-singelton dimension. Default value is us
used if empty.
    gridType = gridType is the type of the grid k. Default value is 0 if k 
is odd-symmetric or 2 if k is even-assymetric-left-shifted. Default value i
is used if empty.

    The function is called by :
    [myIDF, x] = bmIDF(f, k, NZero, nDim, gridType);

    Example : myIDF = bmIDF(f, k);
    Example : myIDF = bmIDF(f, k, [], [],1);
    Example : myIDF = bmIDF(f, k, [], 4, 1);
    Example : myIDF = bmIDF(f, k, [], 4);
    Example : myIDF = bmIDF(f, k, 3*length(x), 4);
    Example : myIDF = bmIDF(f, k, 3*length(x));
    Example : [myIDF, x] = bmIDF(f, k, [], 6);
    Example : [myIDF, x, outGridType] = bmIDF(f, k, [], [], 3).
    """
    f = np.asarray(f)
    
    if gridType is None:
        # Automatically determine gridType based on k and N
        pass

    # Zero-padding
    if NZero > 0:
        f = np.pad(f, ((NZero//2, NZero-NZero//2),) * ndims(f))

    # Apply IFFT based on gridType
    if gridType == 0 or gridType == 2:
        iFf = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(f, axes=nDim), 

                                          axis=nDim))
    
    return iFf
