from __future__ import annotations

import numpy as np


def bmPointReshape(t, *varargin):
    """
    Reshape input to `(nCh_or_dim, nPt)` point format.

    Notes
    -----
    - If input is a row/column vector, it is flattened to 1-D (legacy behavior).
    - If `varargin` is provided, the first value is interpreted as `nCh`.
    """
    if isinstance(t, list):
        return [bmPointReshape(item, *varargin) for item in t]

    arr = np.asarray(t)
    if arr.size == 0:
        return np.array([])

    # Keep historical behavior for vectors: collapse to 1D.
    if arr.ndim == 2 and (arr.shape[0] == 1 or arr.shape[1] == 1):
        return arr.reshape(-1)
    if arr.ndim == 1:
        return arr.reshape(-1)

    if varargin:
        nCh = int(np.asarray(varargin[0]).ravel()[0])
    else:
        nCh = int(arr.shape[0])

    if nCh <= 0 or arr.size % nCh != 0:
        raise ValueError("Input size is not compatible with requested channel/dimension count.")

    nPt = arr.size // nCh
    return arr.reshape(nCh, nPt, order="F")
