import numpy as np

def bmIsBlockShape(x, N_u):
    """
    Check if data x is in block format.

    This function checks if the data in array x is in the block format, i.e
i.e.,
    contains a grid for each channel.
    
    Parameters
    ----------
    x : array-like
        Array of which the format should be tested.
    N_u : array-like
        Size of the data of one channel in x.
    
    Returns
    -------
    bool
        True if x is in block format, False if not.
    """
    x_arr = np.asarray(x)
    N_u_arr = np.asarray(N_u).ravel().astype(int)

    # Quick checks for empty inputs or zero product
    if x_arr.size == 0 or N_u_arr.size == 0:
        return False

    prod_Nu = int(np.prod(N_u_arr))
    if prod_Nu == 0:
        return False

    # MATLAB uses division that may result in a non-integer channel count.
    # If the number of elements is not divisible by prod_Nu, the shape
    # cannot match the expected block shape.
    if x_arr.size % prod_Nu != 0:
        return False

    nCh = x_arr.size // prod_Nu
    expected_shape = tuple(N_u_arr) + (nCh,)
    return x_arr.shape == expected_shape
