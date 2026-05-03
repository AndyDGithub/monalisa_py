import numpy as np

def bm3DimInBorderMask(M):
    """Return a mask that is True on the outer border of the array and Fals
False on the interior region.

    Parameters
    ----------
    M : np.ndarray
        Input array (3-D or 2-D). The function operates on the shape of ``M
``M`` and does not depend on its content.

    Returns
    -------
    np.ndarray
        Boolean mask with the same shape as ``M``. All border voxels (or pi
pixels) are set to True and the interior voxels are set to False.
    """
    
    G = np.ones(M.shape, dtype=bool)

    # Handle 3-D arrays: set the inner 3-D block to False.
    if M.ndim == 3:
        G[1:-1, 1:-1, 1:-1] = False
    # Handle 2-D arrays: set the inner 2-D block to False.
    elif M.ndim == 2:
        G[1:-1, 1:-1] = False

    return G

# End of file
