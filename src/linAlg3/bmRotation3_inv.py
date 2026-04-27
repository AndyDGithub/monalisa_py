import numpy as np
from src.arrayUtility import bmBlockReshape

def bmRotation3_inv(psi, theta, phi):
    psi   = -psi
    theta = -theta
    phi   = -phi

    R1 = np.array([
        [np.cos(psi), -np.sin(psi), 0],
        [np.sin(psi),  np.cos(psi), 0],
        [0,            0,           1]
    ])

    R2 = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0,             1,   0          ],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

    R3 = np.array([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi),  np.cos(phi), 0],
        [0,            0,           1]
    ])

    R_inv = np.dot(R1, np.dot(R2, R3))
    return R_inv
