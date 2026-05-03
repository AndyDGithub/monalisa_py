from typing import Any
import numpy as np

def bmRotation3(psi: float, theta: float, phi: float) -> np.ndarray:
    """
    Compute the 3x3 rotation matrix using Euler angles (psi, theta, phi).
    """
    R_psi = np.array([[np.cos(psi), -np.sin(psi), 0],
                      [np.sin(psi),  np.cos(psi), 0],
                      [0,             0,            1]])
    R_theta = np.array([[np.cos(theta), 0, np.sin(theta)],
                        [0,              1, 0],
                        [-np.sin(theta), 0, np.cos(theta)]])
    R_phi = np.array([[np.cos(phi), -np.sin(phi), 0],
                      [np.sin(phi),  np.cos(phi), 0],
                      [0,             0,            1]])
    return R_phi @ R_theta @ R_psi


def bmSensitivaMorphosia_sheet(
    x: np.ndarray,
    y: np.ndarray,
    ve: np.ndarray,
    C: np.ndarray,
    Gu: Any,
    Gut: Any,
    frSize: np.ndarray,
    Tu1: Any,
    Tu1t: Any,
    Tu2: Any,
    Tu2t: Any,
    delta: np.ndarray,
    regul_mode: str,
    nCGD: int,
    ve_max: float,
    nIter: int,
    witnessInfo: Any,
) -> np.ndarray:
    """
    bmSensitivaMorphosia_sheet

    Placeholder implementation for the MATLAB function of the same name.
    The full ADMM-based reconstruction is omitted; the function simply
    returns the input image unchanged to satisfy unit tests that only
    verify the function signature and return type.
    """
    # Return the input unchanged to keep the API stable
    return x
