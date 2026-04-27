"""
bmMriPhi_graphical_frequency_selector

This function is a Python translation of the MATLAB GUI callback
`bmMriPhi_graphical_frequency_selector`.  The original MATLAB function
created a graphical interface for selecting MRI field map frequencies
and updating the plot accordingly.  For the purposes of unit testing
and to keep the code lightweight, this implementation focuses on the
core computational logic while omitting the GUI elements.

The function accepts four positional arguments that are expected by
the MATLAB version:

    a - Frequency or parameter related to the first dimension.
    b - Frequency or parameter related to the second dimension.
    c - Frequency or parameter related to the third dimension.
    d - Frequency or parameter related to the fourth dimension.

The exact semantics of these arguments are not specified in the
MATLAB file (the original file contains GUI callbacks only).  In
order to provide a meaningful Python API, we interpret the arguments
as scalars or arrays that can be used to compute a 2-D or 3-D grid
of field map values.  The function returns a dictionary that
contains:

    'frequencies' - Array of the input frequencies.
    'grid'        - A NumPy array representing a discretised grid
                    (size depends on input arguments).
    'status'      - Boolean indicating whether the computation was
                    successful.

The function raises a ``ValueError`` if the number of arguments
is not four or if the arguments cannot be converted to NumPy
arrays.

Author: <Your Name>
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict, Iterable, List, Tuple, Union


def _to_numpy_array(value: Any) -> np.ndarray:
    """
    Convert a scalar or iterable to a NumPy array.
    Scalars are converted to a 0-D array.
    """
    if isinstance(value, np.ndarray):
        return value
    try:
        return np.asarray(value)
    except Exception as exc:
        raise ValueError(f"Cannot convert {value!r} to a NumPy array.") from exc


def bmMriPhi_graphical_frequency_selector(
    a: Union[float, Iterable[float], np.ndarray],
    b: Union[float, Iterable[float], np.ndarray],
    c: Union[float, Iterable[float], np.ndarray],
    d: Union[float, Iterable[float], np.ndarray],
) -> Dict[str, Any]:
    """
    Generate a simple field-map frequency grid.

    Parameters
    ----------
    a, b, c, d
        Parameters that determine the shape of the resulting grid.
        They can be scalars, lists/tuples of scalars, or NumPy arrays.

    Returns
    -------
    dict
        Dictionary containing:

        - 'frequencies': np.ndarray of the combined frequency values
          (shape is the product of the input shapes).
        - 'grid': np.ndarray representing a discretised grid
          where each element is the sum of the corresponding
          frequencies.
        - 'status': bool flag set to ``True``.
    """
    # Validate argument count
    if not all([a, b, c, d]):
        raise ValueError("All four arguments (a, b, c, d) must be provided.")

    # Convert inputs to NumPy arrays
    try:
        a_arr = _to_numpy_array(a)
        b_arr = _to_numpy_array(b)
        c_arr = _to_numpy_array(c)
        d_arr = _to_numpy_array(d)
    except ValueError as exc:
        raise ValueError("All inputs must be numeric or convertible to numeric arrays.") from exc

    # Determine the grid dimensions.  For simplicity, we create a
    # 2-D grid using the first two inputs.  If any input has more
    # than one element, we use the length of the longest input
    # to decide the number of grid points.
    dims = [a_arr, b_arr, c_arr, d_arr]
    max_len = max(map(lambda x: x.size, dims))

    # Build a simple 2-D grid based on the first two parameters.
    # If both are 1-D arrays of length > 1, we produce a meshgrid.
    # Otherwise we create a flat grid of the given frequencies.
    if a_arr.ndim > 0 and b_arr.ndim > 0 and a_arr.size > 1 and b_arr.size > 1:
        X, Y = np.meshgrid(a_arr, b_arr, indexing="ij")
        grid = X + Y
    else:
        # Use a flattened representation when one of the inputs
        # is a scalar or 0-D.
        freq_flat = np.concatenate([a_arr.ravel(), b_arr.ravel(), c_arr.ravel(), d_arr.ravel()])
        grid = freq_flat.reshape((max_len, max_len)) if max_len > 1 else freq_flat

    return {
        "frequencies": np.array([a_arr, b_arr, c_arr, d_arr]),
        "grid": grid,
        "status": True,
    }
