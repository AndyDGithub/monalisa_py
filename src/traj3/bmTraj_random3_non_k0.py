import numpy as np

def bmTraj_random3_non_k0(nPt, N_u, dK_u):
    """
    Generate a random 3-D trajectory that avoids the k-space origin.

    This function is a direct port of the MATLAB routine
    ``bmTraj_random3_non_k0``. It creates ``nPt`` random points within a
    rectangular volume defined by the sampling grid sizes ``N_u`` and the
    sampling spacings ``dK_u``. Points that fall within a small sphere arou
around
    the origin (radius ``eps``) are discarded and regenerated until the
    desired number of valid points is obtained.

    Parameters
    ----------
    nPt : int
        Number of trajectory points to generate.
    N_u : array_like, shape (3,)
        Grid dimensions (number of samples) in the three spatial
        directions.
    dK_u : array_like, shape (3,)
        Sampling spacings in the three spatial directions.

    Returns
    -------
    t : ndarray, shape (nPt, 3)
        Random trajectory points.

    Notes
    -----
    The MATLAB implementation uses a while loop that repeatedly generates
    random points and removes those too close to the origin. The same
    logic is preserved here, with a small epsilon ``eps`` defined as
    ``100 * eps`` (machine precision). The algorithm may produce more
    points than requested if many points are discarded; in that case the
    result is truncated to ``nPt`` entries.

    """
    # Ensure input arrays are 1-D with length 3
    N_u = np.asarray(N_u, dtype=np.float64).reshape(3)
    dK_u = np.asarray(dK_u, dtype=np.float64).reshape(3)

    # Half-volume extents
    lx = (N_u[0] - 1) * dK_u[0]
    ly = (N_u[1] - 1) * dK_u[1]
    lz = (N_u[2] - 1) * dK_u[2]

    sx = N_u[0] / 2.0 * dK_u[0]
    sy = N_u[1] / 2.0 * dK_u[1]
    sz = N_u[2] / 2.0 * dK_u[2]

    eps = 100 * np.finfo(float).eps

    # Accumulate valid points
    t = np.empty((0, 3), dtype=np.float64)
    while t.shape[0] < nPt:
        m = nPt - t.shape[0]
        x = np.random.rand(m) * lx - sx
        y = np.random.rand(m) * ly - sy
        z = np.random.rand(m) * lz - sz
        pts = np.column_stack((x, y, z))
        # Keep points that are farther than eps from the origin
        valid = np.linalg.norm(pts, axis=1) > eps
        t = np.vstack((t, pts[valid]))

    # In rare cases we may overshoot; truncate to the requested size
    if t.shape[0] > nPt:
        t = t[:nPt]

    if t.shape[0] != nPt:
        raise ValueError("The output trajectory has incorrect size.")

    return t
