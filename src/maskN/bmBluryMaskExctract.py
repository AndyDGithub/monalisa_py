import numpy as np

def bmBluryMaskExctract(argBluryMask, argArray):
    """Extract elements from `argArray` using a blurring mask.

    Parameters
    ----------
    argBluryMask : np.ndarray
        Blurring mask array.
    argArray : np.ndarray
        Input array to extract elements from.

    Returns
    -------
    tuple
        A tuple containing the extracted elements and the sum (count) of th
th
the mask.
    """
    # Flatten inputs and ensure column vector orientation
    argBluryMask = np.ravel(argBluryMask).T
    argArray = np.ravel(argArray).T

    # Element-wise masking
    masked_array = argArray * argBluryMask

    # Logical mask: treat non-zero entries as True
    logical_mask = np.asarray(argBluryMask, dtype=bool)

    # Extract values where mask is True
    out = masked_array[logical_mask]

    # Count of True elements in mask (MATLAB `sum` on logical array)
    outSum = np.sum(logical_mask)

    return out, outSum
