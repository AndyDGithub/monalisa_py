import numpy as np

def bmNormalVector3(ez):
    """Compute the normal vectors given a vector ez.

    Parameters
    ----------
    ez : array_like, shape (3,)
        The input vector to compute normal vectors from.

    Returns
    -------
    ey : ndarray, shape (3,)
        The first normal vector.
    varargout : list or ndarray
        The second normal vector if `nargout > 1`.
    """
    ez = np.asarray(ez).ravel()
    norm_ez = np.sqrt(np.sum(ez**2))
    if norm_ez == 0:
        raise ValueError("ez must not be zero")
    ez /= norm_ez

    # Sort and permute
    ey, myPerm = np.sort(ez), np.argsort(ez)
    temp = ey[2]
    ey[2] = ey[1]
    ey[1] = -temp
    ey[0] = 0

    norm_ey = np.sqrt(np.sum(ey**2))
    if norm_ey == 0:
        raise ValueError("Normalized ey must not be zero")
    ey /= norm_ey

    ey = ey[myPerm[::-1]]

    # Compute the cross product
    ex = np.cross(ey, ez)
    ex = ex.ravel()

    if len(ex) > 1:
        varargout = [ex]
    else:
        varargout = ex

    return (ey, varargout)
