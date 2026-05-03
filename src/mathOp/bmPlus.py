import numpy as np

def bmPlus(x, y):
    """Element-wise sum of two arrays or lists, mimicking MATLAB's bmPlus.

    Parameters
    ----------
    x : array_like or list of array_like
        First operand.
    y : array_like or list of array_like
        Second operand.

    Returns
    -------
    out : ndarray or list of ndarray
        Element-wise sum of ``x`` and ``y``.  If ``x`` and ``y`` are lists,
lists,
        the result is a list of sums.

    Raises
    ------
    ValueError
        If the inputs are of mixed types (e.g., one is a list and the other
other
        is not) or if two lists have different lengths.
    """
    # Both are lists: element-wise addition
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            raise ValueError("in bmPlus: lists must have same length.")
        return [np.array(xi) + np.array(yi) for xi, yi in zip(x, y)]

    # Neither is a list: direct addition
    if not isinstance(x, list) and not isinstance(y, list):
        return x + y

    # Mixed types are not supported
    raise ValueError("in bmPlus: case not implemented.")
