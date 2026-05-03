import numpy as np

def bmOne(argSize, argType):
    """Create an array of ones with the specified size and type.

    Parameters
    ----------
    argSize : tuple of int
        The shape of the output array.
    argType : str
        The data type of the output array.
        Supported values are:
        - ``real_double``
        - ``complex_double``
        - ``real_single``
        - ``complex_single``

    Returns
    -------
    ndarray
        An array filled with ones in the specified data type and shape.
    """
    if argType == "real_double":
        return np.ones(argSize, dtype=np.float64)
    elif argType == "complex_double":
        return np.ones(argSize, dtype=np.complex128)
    elif argType == "real_single":
        return np.ones(argSize, dtype=np.float32)
    elif argType == "complex_single":
        return np.ones(argSize, dtype=np.complex64)
    else:
        raise ValueError(f"Unsupported type: {argType}")

# ----------------------------------------------------------------------
# MATLAB reference:
# % Bastien Milani
# % CHUV and UNIL
# % Lausanne - Switzerland
# % May 2023
#
# function myOne = bmOne(argSize, argType)
#
# myOne = []; 
# if strcmp(argType, 'real_double')
#     myOne = ones(argSize, 'double'); 
# elseif strcmp(argType, 'complex_double')
#     myOne = complex(ones(argSize, 'double'), zeros(argSize, 'double'));
# elseif strcmp(argType, 'real_single')
#     myOne = ones(argSize, 'single'); 
# elseif strcmp(argType, 'complex_single')
#     myOne = complex(ones(argSize, 'single'), zeros(argSize, 'single'));
# end
#
# end
# ----------------------------------------------------------------------
