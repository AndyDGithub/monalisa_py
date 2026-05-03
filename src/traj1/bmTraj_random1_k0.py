import numpy as np

def bmTraj_random1_k0(nPt: int, N_u: float, dK_u: float) -> np.ndarray:
    """
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023

    Generate a random 1-D trajectory with a guaranteed zero point.

    Parameters
    ----------
    nPt : int
        Number of trajectory points.
    N_u : float
        Undersampling factor (number of points per unit).
    dK_u : float
        K-space sampling step size.

    Returns
    -------
    np.ndarray
        1-D trajectory array of length ``nPt``.
    """
    # MATLAB: myEps = 100*eps; --------------magic_number
    myEps = 100 * np.finfo(float).eps

    # MATLAB: t = rand(1, nPt)*(N_u*dK_u - dK_u) - N_u/2*dK_u;
    t = np.random.rand(1, nPt) * (N_u * dK_u - dK_u) - N_u / 2 * dK_u

    # MATLAB: t = sort(t(:)'); 
    t = np.sort(t.ravel())

    # MATLAB: if sum(abs(t(:)) < myEps) == 0
    if np.sum(np.abs(t) < myEps) == 0:
        # MATLAB: t = [0, t(1, 1:end-1)];
        t = np.hstack((0, t[:-1]))

    # MATLAB: if size(t, 2) ~= nPt
    if t.size != nPt:
        raise ValueError('The output traj has wrong size.')

    return t
