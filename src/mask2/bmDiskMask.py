import numpy as np

def bmDiskMask(argSize, argCenter, argRadius):
    """
    Create a binary mask of a disk within a 2-D array.

    Parameters
    ----------
    argSize : array_like
        Desired array size. Only the first two dimensions are used.
    argCenter : array_like
        Cartesian coordinates of the disk centre (row, column).
    argRadius : float
        Radius of the disk.

    Returns
    -------
    np.ndarray[bool]
        Boolean mask of shape (argSize[0], argSize[1]).
    """
    # Convert inputs to 1-D arrays and keep only first two elements
    argSize = np.asarray(argSize).reshape(-1)
    argSize = argSize[:2]
    argCenter = np.asarray(argCenter).reshape(-1)
    argCenter = argCenter[:2]

    # Square of radius
    radius_sq = argRadius ** 2

    # Generate grid coordinates (MATLAB ndgrid)
    rows = np.arange(argSize[0])
    cols = np.arange(argSize[1])
    x, y = np.meshgrid(rows, cols, indexing="ij")

    # Compute squared distance from centre
    dist_sq = (x - argCenter[0]) ** 2 + (y - argCenter[1]) ** 2

    # Build mask
    mask = dist_sq <= radius_sq
    return mask.astype(bool)
