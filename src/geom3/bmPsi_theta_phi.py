import numpy as np

from src.geom3.bmTheta_phi import bmTheta_phi

__all__ = ["bmPsi_theta_phi"]

def bmPsi_theta_phi(R):
    """
    Compute Euler angles (psi, theta, phi) from a rotation matrix R.
    Parameters
    ----------
    R : array-like, shape (3,3) or (9,)
        Rotation matrix.
    Returns
    -------
    psi : float
        First Euler angle (rotation about z-axis).
    theta : float
        Second Euler angle (rotation about y-axis).
    phi : float
        Third Euler angle (rotation about z-axis).
    """
    R = np.asarray(R)
    if R.shape == (9,):
        R = R.reshape((3,3))
    elif R.shape != (3,3):
        raise ValueError("R must be a 3x3 matrix or array of length 9")

    # Extract third column
    n_col = R[:, 2]
    theta, phi = bmTheta_phi(n_col)

    # Determine if we are in a gimbal lock situation
    eps = np.finfo(float).eps
    cos_theta = np.cos(theta)
    if 1 - np.abs(cos_theta) > eps:
        # Not in gimbal lock, compute psi from the third row
        _, psi = private_theta_psi(R[2, :])
    else:
        # Gimbal lock: compute psi from first column
        psi = private_psi(R[:, 0], cos_theta)

    # Ensure angles are in [0, 2π)
    if phi < 0:
        phi += 2 * np.pi
    if psi < 0:
        psi += 2 * np.pi

    return psi, theta, phi

def private_theta_psi(n):
    """
    Compute psi angle when we are not in a gimbal lock situation.
    n is the third row of the rotation matrix.
    """
    eps = np.finfo(float).eps
    n = np.asarray(n).reshape(3)

    sin_theta = np.sqrt(n[0]**2 + n[1]**2)
    # Gimbal lock occurs when sin_theta is zero (i.e., n[2] ~ ±1)
    if sin_theta > eps:
        cos_psi = -n[0] / sin_theta
        sin_psi = n[1] / sin_theta
        # Normalize (cos_psi, sin_psi)
        norm_factor = np.sqrt(cos_psi**2 + sin_psi**2)
        cos_psi /= norm_factor
        sin_psi /= norm_factor
        psi = np.angle(complex(cos_psi, sin_psi))
    else:
        psi = 0.0
    return 0.0, psi  # The first return value is unused; mimic MATLAB signature

def private_psi(n, cos_theta):
    """
    Compute psi angle in the gimbal lock case.
    n is the first column of the rotation matrix.
    """
    n = np.asarray(n).reshape(3)
    n = n / np.linalg.norm(n)

    if cos_theta > 0:
        psi = np.angle(complex(n[0], n[1]))
    else:
        psi = np.angle(complex(-n[0], n[1]))
    return psi
