import numpy as np
from src.linAlg3.bmRotation3 import bmRotation3

def bmOmega3(psi, theta, phi):
    R_psi = bmRotation3(psi, 0, 0)
    R_theta = bmRotation3(0, theta, 0)
    R_phi = bmRotation3(0, 0, phi)

    omega_psi = np.array([[-np.sin(psi), -np.cos(psi), 0],
                          [np.cos(psi), -np.sin(psi), 0],
                          [0, 0, 0]])
    omega_theta = np.array([[-np.sin(theta), 0, np.cos(theta)],
                            [0, 0, 0],
                            [-np.cos(theta), 0, -np.sin(theta)]])
    omega_phi = np.array([[-np.sin(phi), -np.cos(phi), 0],
                          [np.cos(phi), -np.sin(phi), 0],
                          [0, 0, 0]])

    omega_psi = R_phi @ R_theta @ omega_psi
    omega_theta = R_phi @ omega_theta @ R_psi.T
    omega_phi = omega_phi @ R_theta @ R_psi.T

    return (omega_psi, omega_theta, omega_phi)
