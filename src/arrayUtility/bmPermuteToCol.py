from __future__ import annotations
import numpy as np

def bmPermuteToCol(y, argSize=None, *varargin):
    """
    Convert data into column-major format.

    Parameters
    ----------
    y : array-like or list
        Data to permute. If a list, the operation is applied recursively.
    argSize : int, array-like or None, optional
        Desired number of rows for the output. If None, the size is inferre
inferred
        from the input.
    *varargin : optional
        Additional size arguments (scalar or iterable) to be interpreted
        as the desired row count.

    Returns
    -------
    out : array-like or list
        Permuted data. Lists are returned for list inputs.
    """
    # Combine all size arguments into a single list
    size_args = []
    if argSize is not None:
        size_args.append(argSize)
    size_args.extend(varargin)
    argSizeList = bmVarargin(*size_args)

    # Work recursively if y is a list
    if isinstance(y, list):
        return [bmPermuteToCol(item, *argSizeList) for item in y]

    # Return empty array if y is empty
    if len(y) == 0:
        return []

    # Determine number of channels and points
    if not argSizeList:
        nCh = len(y)
        nPt = len(y[0]) // nCh
    else:
        nPt = np.prod(argSizeList)
        nCh = len(y) // nPt

    y_arr = np.array(y).reshape(nCh, nPt)
    return y_arr.T


def bmVarargin(*args):
    """
    Distribute positional arguments with None padding for missing entries.

    Mirrors MATLAB's bmVarargin(varargin) which returns the elements of the
the
    cell array varargin{} and fills missing outputs with [].

    Parameters
    ----------
    *args : any
        Positional arguments to be collected.

    Returns
    -------
    list
        List of arguments.
    """
    return list(args)
