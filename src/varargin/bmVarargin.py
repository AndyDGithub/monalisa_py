def bmVarargin(*args):
    """
    MATLAB-like varargin helper.

    Returns inputs as a plain list so callers can unpack manually.
    """
    return list(args)


def bmVarargin_unpack(args_list, n):
    """
    Unpack args_list to exactly n values, padding with None.
    """
    result = list(args_list) if args_list else []
    while len(result) < n:
        result.append(None)
    return result[:n]


__all__ = ["bmVarargin", "bmVarargin_unpack"]
