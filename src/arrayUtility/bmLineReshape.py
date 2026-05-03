import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmLineReshape(argIn, argSize):
    """Reshape a signal into a matrix with specified dimensions.

    This function reshapes an input array or cell array into a 3D matrix
    with the given number of channels (nCh), lines (N), and samples per lin
line
    (nLine).

    Parameters
    ----------
    argIn : array_like or list of array_like
        Input signal to be reshaped.
    argSize : tuple of int
        A tuple containing three integers (nCh, N, nLine) specifying the di
dimensions of the output matrix.

    Returns
    -------
    out : ndarray
        The reshaped 3D numpy array.
    """
    
    # If a list is provided, recursively reshape each element.
    if isinstance(argIn, list):
        return [bmLineReshape(item, argSize) for item in argIn]
    
    # Handle array of objects (cell array analogue).
    if isinstance(argIn, np.ndarray) and argIn.dtype == object:
        out = np.empty_like(argIn)
        for i, item in enumerate(argIn.ravel()):
            out.ravel()[i] = bmLineReshape(item, argSize)
        return out
    
    # Convert input to a numpy array.
    argIn = np.asarray(argIn)
    
    # Ensure argSize is a 1-D array of integers.
    argSize = np.array(argSize).ravel().astype(int)
    nCh = int(argSize[0])
    N = int(argSize[1])
    
    # Compute the number of samples per line (must be an integer).
    nLine = argIn.size // nCh // N
    return argIn.reshape(nCh, N, nLine)
