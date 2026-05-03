# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np


def bmRotation2_inv(phi):
    """Compute the inverse of a 2D rotation matrix.

    Parameters
    ----------
    phi : float
        Angle in radians to rotate counterclockwise.

    Returns
    -------
    R_inv : ndarray
        The inverse (clockwise) rotation matrix.
    """
    phi = -phi
    R_inv = np.array(
        [
            [np.cos(phi), -np.sin(phi)],
            [np.sin(phi), np.cos(phi)],
        ]
    )
    return R_inv
