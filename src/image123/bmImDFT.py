import numpy as np
from src.fourierN.bmDFT import bmDFT
from src.imageN.bmImDim import bmImDim

def bmImDFT(argIm, dummy=None, *varargin):
    """
    MATLAB: function [Ff, varargout] = bmImDFT(argIm, varargin)
    Performs a zero-padded DFT along each dimension of an image.

    Parameters
    ----------
    argIm : ndarray
        Input image of arbitrary dimensionality.
    dummy : optional
        Placeholder positional argument to match MATLAB arity.
    *varargin : optional
        nZero_x, nZero_y, nZero_z for 1-, 2-, and 3-D data.
        Missing values are treated as empty (no zero padding).

    Returns
    -------
    tuple
        (Ff, (kx, ky, kz))  for 1-3D data
        (Ff, (kx, ky, kz, kxyz_block))  for higher dimensions
    """
    nZero_x = varargin[0] if len(varargin) > 0 else None
    nZero_y = varargin[1] if len(varargin) > 1 else None
    nZero_z = varargin[2] if len(varargin) > 2 else None

    kx = None
    ky = None
    kz = None

    myDim = bmImDim(argIm)

    if myDim == 1:
        Ff, kx = bmDFT(argIm, 1, nZero_x, 1)
    elif myDim == 2:
        Ff, kx = bmDFT(argIm, 1, nZero_x, 1)
        Ff, ky = bmDFT(Ff, 1, nZero_y, 2)
    elif myDim == 3:
        Ff, kx = bmDFT(argIm, 1, nZero_x, 1)
        Ff, ky = bmDFT(Ff, 1, nZero_y, 2)
        Ff, kz = bmDFT(Ff, 1, nZero_z, 3)
    else:
        # For dimensions higher than 3, perform DFT along each dimension
        Ff = argIm
        k_vectors = []
        for dim in range(1, myDim + 1):
            Ff, k = bmDFT(Ff, 1, None, dim)
            k_vectors.append(k)
        kx, ky, kz = k_vectors[0], k_vectors[1], k_vectors[2]
        # For higher dimensions, return block reshaped k vectors
        from src.arrayUtility.bmBlockReshape import bmBlockReshape
        kxyz = np.stack((kx, ky, kz), axis=-1)
        return Ff, (kx, ky, kz, bmBlockReshape(kxyz, myDim))

    kxyz = np.stack((kx, ky, kz), axis=-1)
    return Ff, (kx, ky, kz) if myDim < 4 else (kx, ky, kz, kxyz)



# src/varargin/bmVarargin.py

import numpy as np

def bmVarargin(*args):
    """
    Distribute positional arguments with None padding for missing entries.
    
    Mirrors MATLAB's bmVarargin(varargin) which returns the elements of the
the
    cell array varargin{} and fills missing outputs with [].
    
    Usage:
        C, N_u, n_u, dK_u = bmVarargin(C, N_u, n_u)      # dK_u = None
        C, N_u              = bmVarargin(C)                # N_u = None
        vals                = bmVarargin(a, b, c)          # returns [a, b,
b, c]
    """
    return list(args)

def bmVarargin_unpack(args_list, n):
    """Unpack args_list to exactly n values, padding with None."""
    result = list(args_list) if args_list else []
    while len(result) < n:
        result.append(None)
    return result[:n]
