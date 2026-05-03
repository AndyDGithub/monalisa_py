import numpy as np
from src.arrayUtility import bmBlockReshape

def bmMinus(x, y):
    """
    Compute the difference between two arrays or lists of arrays.

    The function emulates MATLAB's behaviour:
    * If both arguments are cell/ lists, element-wise subtraction.
    * If one argument is a single array and the other a list, subtract the 
single array from each element of the list.
    * If both are single arrays, perform a straightforward subtraction.

    Parameters
    ----------
    x : array_like or list of array_like
        First input.
    y : array_like or list of array_like
        Second input.

    Returns
    -------
    out : array_like or list of array_like
        The element-wise difference, reshaped with bmBlockReshape.
    """
    # Helper to convert a single array to numpy array
    def _to_arr(a):
        return np.asarray(a)

    # Case 1: both are lists
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            raise ValueError("In bmMinus : list sizes differ.")
        out = [None] * len(x)
        for i in range(len(x)):
            out[i] = bmBlockReshape(_to_arr(x[i]) - _to_arr(y[i]))
        return out

    # Case 2: both are single arrays
    if not isinstance(x, list) and not isinstance(y, list):
        return bmBlockReshape(_to_arr(x) - _to_arr(y))

    # Case 3: x single, y list
    if not isinstance(x, list) and isinstance(y, list):
        out = [None] * len(y)
        for i in range(len(y)):
            out[i] = bmBlockReshape(_to_arr(x) - _to_arr(y[i]))
        return out

    # Case 4: x list, y single (not in MATLAB but supported)
    if isinstance(x, list) and not isinstance(y, list):
        out = [None] * len(x)
        for i in range(len(x)):
            out[i] = bmBlockReshape(_to_arr(x[i]) - _to_arr(y))
        return out

    # Should never reach here
    raise ValueError("In bmMinus : case not implemented.")
