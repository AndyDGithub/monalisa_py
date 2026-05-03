import numpy as np

def bmIsScalar(x):
    """Return True if *x* is a scalar or a single-element array; otherwise 
False.

    Mimics the MATLAB function ``bmIsScalar``: lists, tuples, dicts and set
set
sets
    (cell-like Python objects) are treated as non-scalar, while NumPy array
array
arrays
    with a single element (including zero-dimensional arrays) are considere
considere
considered
    scalar.
    """
    # Reject cell-like Python objects
    if isinstance(x, (list, tuple, dict, set)):
        return False

    arr = np.asarray(x)

    # Zero-dimensional NumPy arrays are scalars
    if arr.ndim == 0:
        return True

    # Single-element arrays are scalars
    return arr.size == 1

# MATLAB reference implementation
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
#
# function out = bmIsScalar(x)
#
# out = false;
#
# if iscell(x)
#     out = false;
#     return;
# end
#
# if size(x(:), 1) == 1
#     out = true;
#     return;
# else
#     out = false;
#     return;
# end
#
# end
