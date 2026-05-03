import numpy as np


def bmBlockReshape(argIn, N_u):
    """Reshape flat/stacked data to block format (N_u..., nCh)."""
    if isinstance(argIn, list):
        return [bmBlockReshape(item, N_u) for item in argIn]

    arr = np.asarray(argIn)
    if arr.size == 0:
        return np.array([])

    N_u = np.asarray(N_u, dtype=int).ravel()
    if N_u.size == 0:
        raise ValueError("N_u must contain at least one dimension")

    nPt = int(np.prod(N_u))
    if arr.size % nPt != 0:
        raise ValueError("argIn size is not compatible with N_u")

    nCh = arr.size // nPt
    return arr.reshape(tuple(N_u) + (nCh,))
