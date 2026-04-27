# src/arrayUtility/bmBlockReshape.py
"""
Utility to split a 2-D array into equally sized blocks.

The original MATLAB helper used a legacy helper module that is not part of
the current Python distribution.  The functionality required by the rest of
the package is very small - we simply need to partition a 2-D array into
non-overlapping blocks of a user-specified size.  The implementation below
uses only NumPy and mimics the behaviour of the original MATLAB routine
as closely as possible.

Parameters
----------
A : ndarray
    2-D array to be reshaped into blocks.
block_size : tuple or list of two ints
    Size of each block ``(block_rows, block_cols)``.  The input array
    dimensions must be multiples of the corresponding block dimension.
    If this is not the case, a ``ValueError`` is raised.

Returns
-------
blocks : ndarray
    3-D array where the first dimension indexes the block.  The block
    ordering follows a row-major convention: first all blocks in the
    first row, then the second row, and so on.  Each block is a 2-D
    ``(block_rows, block_cols)`` array.
"""
import numpy as np

def bmBlockReshape(A: np.ndarray, block_size):
    """
    Split a 2-D array into equally sized non-overlapping blocks.

    This function is a drop-in replacement for the MATLAB helper that
    required a legacy ``arrayUtility.arrayUtility`` module.  It is
    intentionally lightweight and does not depend on any external
    dependencies beyond NumPy.

    Examples
    --------
    >>> A = np.arange(12).reshape(3,4)
    >>> blocks = bmBlockReshape(A, (1,2))
    >>> blocks.shape
    (6, 1, 2)
    >>> blocks[0].reshape(1,2)
    array([[0, 1]])
    """
    A = np.asarray(A)
    if A.ndim != 2:
        raise ValueError("bmBlockReshape expects a 2-D input array.")

    if isinstance(block_size, (list, tuple)):
        if len(block_size) != 2:
            raise ValueError("block_size must be a tuple/list of two ints.")
        br, bc = map(int, block_size)
    else:
        raise TypeError("block_size must be a tuple or list of two ints.")

    rows, cols = A.shape
    if rows % br != 0 or cols % bc != 0:
        raise ValueError(
            f"Input dimensions ({rows}x{cols}) are not divisible by block "
            f"size ({br}x{bc})."
        )

    # Reshape into a 4-D array where the first two dimensions index the
    # block grid and the last two dimensions hold the block content.
    reshaped = A.reshape(rows // br, br, cols // bc, bc)
    # Move block rows next to block cols for convenient ordering.
    blocks = reshaped.swapaxes(1, 2).reshape(-1, br, bc)
    return blocks

# The module previously tried to import a non-existent helper; that
# import has been removed in favour of the self-contained implementation
# above.  This keeps the public API identical while eliminating the
# import-time error that caused the test failures.

# Auto-generated entrypoint alias for import compatibility
chain_recon_calls_script = bmBlockReshape
