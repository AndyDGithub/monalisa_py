import numpy as np

def bmRotation3(psi, theta, phi):
    """
    Compute a 3*3 rotation matrix from Euler angles (psi, theta, phi).

    Parameters
    ----------
    psi : float
        Third elementary rotation about the Z axis.
    theta : float
        Second elementary rotation about the Y axis.
    phi : float
        First elementary rotation about the Z axis.

    Returns
    -------
    np.ndarray
        The 3*3 rotation matrix R = Z(phi)·Y(theta)·Z(psi).
    """
    # Rotation about Z by psi
    R_psi = np.array([
        [np.cos(psi), -np.sin(psi), 0.0],
        [np.sin(psi),  np.cos(psi), 0.0],
        [0.0,          0.0,         1.0]
    ])

    # Rotation about Y by theta
    R_theta = np.array([
        [np.cos(theta), 0.0, np.sin(theta)],
        [0.0,           1.0, 0.0          ],
        [-np.sin(theta),0.0, np.cos(theta)]
    ])

    # Rotation about Z by phi
    R_phi = np.array([
        [np.cos(phi), -np.sin(phi), 0.0],
        [np.sin(phi),  np.cos(phi), 0.0],
        [0.0,          0.0,         1.0]
    ])

    # Compose the rotations
    R = R_phi @ R_theta @ R_psi
    return R
import numpy as np
from third_part.matlab_compat.matlab_native import double

def bmTraj_random2_non_k0(nPt, N_u, dK_u):
    """Generate a 2-D random trajectory that never visits the origin.

    Parameters
    ----------
    nPt : int
        Number of trajectory points to generate.
    N_u : array_like
        1*2 vector of undersampling grid sizes (columns first, rows second)
second).
    dK_u : array_like
        1*2 vector of k-space sampling spacings (columns first, rows second
second).

    Returns
    -------
    ndarray
        Array of shape (nPt, 2) with (x, y) coordinates.
    """
    # 1: safety margin to avoid the origin
    myEps = 100 * np.finfo(float).eps

    # Ensure column vectors as in MATLAB
    N_u = double(N_u.ravel().T)
    dK_u = double(dK_u.ravel().T)

    # Compute k-space extents
    lx = (N_u[0, 0] - 1) * dK_u[0, 0]
    ly = (N_u[0, 1] - 1) * dK_u[0, 1]
    sx = N_u[0, 0] / 2 * dK_u[0, 0]
    sy = N_u[0, 1] / 2 * dK_u[0, 1]

    # Generate initial random points
    x = (np.random.rand(1, nPt) * lx) - sx
    y = (np.random.rand(1, nPt) * ly) - sy
    t = np.vstack((x.flatten(), y.flatten())).T

    # Reject points too close to the origin
    n = np.sqrt(t[:, 0] ** 2 + t[:, 1] ** 2)
    m = (n < myEps)
    while np.any(m):
        # Re-sample only the rejected points
        new_x = np.random.rand(nPt) * lx - sx
        new_y = np.random.rand(nPt) * ly - sy
        new_n = np.sqrt(new_x ** 2 + new_y ** 2)
        t[~m, :] = np.vstack((new_x[~m], new_y[~m])).T
        n[~m] = new_n[~m]
        m = (n < myEps)

    # Final sanity check
    if t.shape[0] != nPt:
        raise ValueError("The output trajectory has wrong size.")
    return t
