# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np


def bmNumOfDim(a):
    """
    Return the number of dimensions of array `a`, mimicking MATLAB's ndims
    with special handling for 2-D arrays.

    MATLAB equivalent:

        n = ndims(a);
        s = size(a);
        s = s(:)'; 

        if n == 2
            if min(s(:)) == 0
                n = 0;
            elseif min(s(:)) == 1
                n = 1;
            else
                n = 2;
            end
        end
    """
    arr = np.asarray(a)
    # Treat scalars and empty arrays as 2-D for parity with MATLAB
    if arr.ndim == 0:
        shape = (1, 1)
        n = 2
    else:
        shape = arr.shape
        n = arr.ndim

    if n == 2:
        min_dim = min(shape)
        if min_dim == 0:
            n = 0
        elif min_dim == 1:
            n = 1
        else:
            n = 2
    return n
