import numpy as np


def bmIndex2MultiIndex(argInd, argSize):
    """
    Convert a linear index to a multi-dimensional index.

    Parameters
    ----------
    argInd : int
        Linear index (1-based) to convert.
    argSize : array_like
        Size of each dimension of the array.

    Returns
    -------
    outInd : ndarray
        Multi-dimensional index (1-based) corresponding to ``argInd``.

    Notes
    -----
    The function follows MATLAB's column-major ordering.  The implementatio
implementation
    mirrors the original MATLAB algorithm: a leading 1 is added to the size
size
    vector to simplify cumulative product calculation, the linear index
index is
    adjusted to zero-based, and then the multi-index is recovered by succes
successive
    integer divisions.

    Example
    -------
    >>> bmIndex2MultiIndex(5, [2, 3])
    array([1, 3])
    """
    # Ensure integer linear index
    myInd = int(argInd) - 1

    # Flatten size vector to 1-D integer array
    mySize = np.array(argSize).ravel().astype(int)

    # Number of dimensions
    L = len(mySize)

    # Extend size with leading 1 for cumulative product computation
    mySize_ext = np.concatenate(([1], mySize))

    # Compute cumulative products: P[i] = prod(mySize_ext[:i+1])
    P = np.empty(L, dtype=int)
    for i in range(L):
        P[i] = int(np.prod(mySize_ext[: i + 1]))

    # Initialize output index array
    outInd = np.zeros(L, dtype=int)

    # Convert linear index to multi-dimensional index
    for i in range(L):
        j = L - 1 - i
        temp_ind = int(myInd // P[j])
        outInd[j] = temp_ind
        myInd -= temp_ind * P[j]

    # Convert back to 1-based indexing
    outInd += 1
    return outInd

__all__ = ["bmIndex2MultiIndex"]
