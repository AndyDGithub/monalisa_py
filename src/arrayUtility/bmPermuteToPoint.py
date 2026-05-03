import numpy as np

def bmPermuteToPoint(y, argSize):
    """Permutes the input data to a point form.

    MATLAB equivalent:
        out = bmPermuteToPoint(y, argSize)
    """
    # Handle cell/array of cells
    if isinstance(y, list):
        return [bmPermuteToPoint(item, argSize) for item in y]
    if isinstance(y, np.ndarray) and y.dtype == object:
        out = np.empty_like(y)
        for i, item in enumerate(y.ravel()):
            out.ravel()[i] = bmPermuteToPoint(item, argSize)
        return out

    # Convert to array
    y = np.asarray(y)
    if y.size == 0:
        return np.array([])

    nPt = int(np.prod(np.array(argSize).ravel()))
    nCh = y.size // nPt
    return y.reshape(nPt, nCh).T
