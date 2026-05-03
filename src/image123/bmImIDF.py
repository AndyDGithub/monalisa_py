import numpy as np
from src.fourierN.bmIDF import bmIDF
from src.imageN.bmImDim import bmImDim

def bmImIDF(argIm, *varargin):
    """
    Compute the inverse Fourier transform of an image with optional zero pa
padding.
    
    Parameters
    ----------
    argIm : np.ndarray
        The input image.
    *varargin : tuple
        Optional zero padding values for the x, y, and z dimensions. If not
not
        provided, the corresponding padding is assumed to be 0.
    
    Returns
    -------
    np.ndarray
        The computed inverse Fourier transform of the image.
    """
    # Extract padding values
    nZero_x = None
    nZero_y = None
    nZero_z = None
    if len(varargin) > 0:
        nZero_x = varargin[0]
    if len(varargin) > 1:
        nZero_y = varargin[1]
    if len(varargin) > 2:
        nZero_z = varargin[2]
    
    # Convert to integers if provided
    nZero_x = int(nZero_x) if nZero_x is not None else 0
    nZero_y = int(nZero_y) if nZero_y is not None else 0
    nZero_z = int(nZero_z) if nZero_z is not None else 0
    
    myDim = bmImDim(argIm)
    
    if myDim == 1:
        iFf = bmIDF(argIm, 1, nZero_x, 1)
        iFf = iFf / argIm.shape[0]
    elif myDim == 2:
        iFf = bmIDF(argIm, 1, nZero_x, 1)
        iFf = bmIDF(iFf, 1, nZero_y, 2)
        iFf = iFf / argIm.shape[0]
        iFf = iFf / argIm.shape[1]
    elif myDim == 3:
        iFf = bmIDF(argIm, 1, nZero_x, 1)
        iFf = bmIDF(iFf, 1, nZero_y, 2)
        iFf = bmIDF(iFf, 1, nZero_z, 3)
        iFf = iFf / argIm.shape[0]
        iFf = iFf / argIm.shape[1]
        iFf = iFf / argIm.shape[2]
    else:
        raise ValueError("Unsupported dimension")
    
    return iFf
