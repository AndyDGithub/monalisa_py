import numpy as np

def bmTraj_random2_k0(nPt, N_u, dK_u):
    """Generate a 2D random trajectory.

    Parameters
    ----------
    nPt : int
        Number of trajectory points.
    N_u : array_like
        1x2 array of undersampling factors.
    dK_u : array_like
        1x2 array of k-space step sizes.

    Returns
    -------
    np.ndarray
        2xN array of trajectory coordinates.
    """
    # MATLAB: myEps = 100*eps
    myEps = 100 * np.finfo(float).eps

    # Ensure inputs are 1x2 arrays
    N_u = np.asarray(N_u).reshape(1, 2).astype(float)
    dK_u = np.asarray(dK_u).reshape(1, 2).astype(float)

    lx = (N_u[0, 0] - 1) * dK_u[0, 0]
    ly = (N_u[0, 1] - 1) * dK_u[0, 1]
    sx = N_u[0, 0] / 2 * dK_u[0, 0]
    sy = N_u[0, 1] / 2 * dK_u[0, 1]

    # Random points in the range [-sx, lx-sx] and [-sy, ly-sy]
    x = (np.random.rand(nPt) * lx) - sx
    y = (np.random.rand(nPt) * ly) - sy

    t = np.vstack((x, y))  # shape (2, nPt)

    n = np.sqrt(t[0, :] ** 2 + t[1, :] ** 2)
    m = n < myEps

    if not np.any(m):
        # MATLAB: t = cat(2, [0;0], t(:,1:end-1));
        zero_col = np.array([[0.0], [0.0]])  # shape (2,1)
        t = np.concatenate((zero_col, t[:, :-1]), axis=1)

    if t.shape[1] != nPt:
        raise ValueError('The output traj has wrong size.')

    return t
