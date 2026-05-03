import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmBigDoor_function(x, L, a):
    """
    Implements a binary step function.

    The MATLAB implementation defines
        f = zeros(size(x));
        f((x-a) >= -L/2) = 1;
        f((x-a) >=  L/2) = 0;
    This returns 1 for -L/2 <= x-a < L/2 and 0 elsewhere.
    """
    f = np.zeros_like(x)
    mask1 = (x - a) >= -L / 2
    f[mask1] = 1
    mask2 = (x - a) >= L / 2
    f[mask2] = 0
    return f
