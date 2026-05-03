import numpy as np


"""
bmRand

This function generates random matrices of various numeric types, mirroring
mirroring MATLAB's
`rand` and `complex` construction.  The MATLAB reference:

% Bastien Milani
% CHUV and UNIL
% Lausanne - Switzerland
% May 2023
%
% function z = bmRand(argSize, argType)
%
% z = [];
% if strcmp(argType, 'real_double')
%     z = rand(argSize, 'double');
% elseif strcmp(argType, 'complex_double')
%     z = complex(rand(argSize, 'double'), rand(argSize, 'double'));
% elseif strcmp(argType, 'real_single')
%     z = rand(argSize, 'single');
% elseif strcmp(argType, 'complex_single')
%     z = complex(rand(argSize, 'single'), rand(argSize, 'single'));
% end
%
"""


def bmRand(argSize, argType):
    """
    Generate a random array matching the requested MATLAB type.

    Parameters
    ----------
    argSize : int or iterable of ints
        Desired shape of the output array.
    argType : str
        One of 'real_double', 'complex_double', 'real_single', 'complex_sin
'complex_single'.
        The default (unknown type) produces a real double array.

    Returns
    -------
    np.ndarray
        Randomly generated array with the specified shape and dtype.
    """
    # Ensure argSize is a tuple of integers
    argSize = tuple(np.array(argSize).ravel().astype(int))

    if argType == "real_double":
        return np.random.rand(*argSize)
    elif argType == "complex_double":
        return np.random.rand(*argSize) + 1j * np.random.rand(*argSize)
    elif argType == "real_single":
        return np.random.rand(*argSize).astype("float32")
    elif argType == "complex_single":
        return (
            np.random.rand(*argSize) + 1j * np.random.rand(*argSize)
        ).astype("complex64")
    # Default to real double if an unknown type is given
    return np.random.rand(*argSize)
