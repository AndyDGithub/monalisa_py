import numpy as np
from src.arrayUtility import bmBlockReshape

def bmRotation3(psi, theta, phi):
    """Auto-generated from MATLAB source. Review manually before production use."""

    # Define rotation matrices based on Euler angles
    R_psi = np.array([
        [np.cos(psi), -np.sin(psi), 0],
        [np.sin(psi), np.cos(psi), 0],
        [0, 0, 1]
    ])

    R_theta = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

    R_phi = np.array([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi), np.cos(phi), 0],
        [0, 0, 1]
    ])

    # Calculate rotation matrix
    R = R_phi @ R_theta @ R_psi

    return R
