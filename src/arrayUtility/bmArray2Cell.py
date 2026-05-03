# ----------------------------------------------------------------------------------------------------------------------------------------------------

def bmArray2Cell(a, N_u):
    """
    Convert an N-dimensional array to a cell array (array of numpy arrays).
arrays).

    Parameters
    ----------
    a : ndarray
        Input array of arbitrary shape.
    N_u : array_like
        Array of indices that define how many leading dimensions of ``a`` a
are
        treated as cell indices. The length of ``N_u`` determines the numbe
number of
        leading dimensions to split into cells.

    Returns
    -------
    c : ndarray of object
        A cell-like array (numpy array of dtype object) where each element
        corresponds to a subarray of ``a`` defined by the leading dimension
dimension
        indices.

    Notes
    -----
    The function preserves the behavior of MATLAB's ``cell`` construction,
    including collapsing trailing singleton dimensions when necessary.
    """
    nDim_array = int(np.size(N_u))
    a = np.asarray(a)
    a_size = a.shape
    in_size = a_size[:nDim_array]
    in_length = int(np.prod(in_size)) if in_size else 1
    c_size = a_size[nDim_array:]
    if len(c_size) <= 1:
        c_size = tuple(c_size) + (1,) if c_size else (1,)
    c_length = int(np.prod(c_size))
    a = a.reshape(in_length, c_length)
    c = np.empty(c_length, dtype=object)
    for i in range(c_length):
        c[i] = a[:, i].reshape(in_size)
    c = c.reshape(c_size)
    return c
