from __future__ import annotations
import numpy as np


def bmPermuteToCol(y, argSize=None, *varargin):
    """Convert data to point-major layout (nPt, nCh)."""
    size_args = []
    if argSize is not None:
        size_args.append(argSize)
    size_args.extend(varargin)

    if isinstance(y, list):
        return [bmPermuteToCol(item, *size_args) for item in y]

    arr = np.asarray(y)
    if arr.size == 0:
        return np.array([])

    if not size_args:
        # Default convention used in the codebase: input is (nCh, nPt).
        if arr.ndim == 1:
            return arr.reshape(-1, 1)
        return arr.reshape(arr.shape[0], -1).T

    nPt = int(np.prod(np.asarray(size_args, dtype=int).ravel()))
    if nPt <= 0 or arr.size % nPt != 0:
        raise ValueError("Input size is not compatible with argSize")
    nCh = arr.size // nPt
    return arr.reshape(nPt, nCh)


def bmVarargin(*args):
    return list(args)
