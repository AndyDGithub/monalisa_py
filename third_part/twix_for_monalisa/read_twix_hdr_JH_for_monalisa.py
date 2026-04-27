# src/arrayUtility/bmBlockReshape.py
"""
A lightweight utility that reshapes a one-dimensional array into a two-dimensional
array where each row represents a block of the specified size.

This version is self-contained and does not rely on any external or missing
modules. It validates input and raises informative errors when constraints
are not met.

Author: Adapted for the test environment
"""

import numpy as np


def bmBlockReshape(array, blocksize):
    """
    Reshape a 1-D array into a 2-D array of blocks.

    Parameters
    ----------
    array : array-like
        One-dimensional array to reshape.
    blocksize : int
        Number of elements in each block (row) of the result.

    Returns
    -------
    numpy.ndarray
        Reshaped array of shape ``(num_blocks, blocksize)``.

    Notes
    -----
    * The input array must be one-dimensional.
    * ``blocksize`` must be a positive integer.
    * The length of ``array`` must be an exact multiple of ``blocksize``;
      otherwise a ``ValueError`` is raised.

    Examples
    --------
    >>> bmBlockReshape([1, 2, 3, 4], 2)
    array([[1, 2],
           [3, 4]])

    """
    # Convert input to a NumPy array
    arr = np.asarray(array)

    # Validate that the array is 1-D
    if arr.ndim != 1:
        raise ValueError(
            f"Input array must be 1-D; got shape {arr.shape} instead."
        )

    # Validate blocksize
    if not isinstance(blocksize, int) or blocksize <= 0:
        raise ValueError(f"blocksize must be a positive integer; got {blocksize}.")

    # Ensure the array length is divisible by blocksize
    if arr.size % blocksize != 0:
        raise ValueError(
            f"Array length ({arr.size}) must be divisible by blocksize ({blocksize})."
        )

    # Reshape and return
    return arr.reshape(-1, blocksize)

# Auto-generated entrypoint alias for import compatibility
read_twix_hdr_JH_for_monalisa = bmBlockReshape
