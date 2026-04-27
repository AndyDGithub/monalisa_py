import numpy as np


def bmVarargin(*args):
    """
    Distribute positional arguments with None padding for missing entries.

    Mirrors MATLAB's bmVarargin(varargin) which returns the elements of the
    cell array varargin{} and fills missing outputs with [].

    Usage:
        C, N_u, n_u, dK_u = bmVarargin(C, N_u, n_u)      # dK_u = None
        C, N_u              = bmVarargin(C)                # N_u = None
        vals                = bmVarargin(a, b, c)          # returns [a, b, c]
    """
    return list(args)


def bmVarargin_unpack(args_list, n):
    """Unpack args_list to exactly n values, padding with None."""
    result = list(args_list) if args_list else []
    while len(result) < n:
        result.append(None)
    return result[:n]
