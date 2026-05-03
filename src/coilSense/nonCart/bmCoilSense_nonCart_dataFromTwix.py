class bmTraj:
        def __init__(self, *args, **kwargs):
            pass

def bmRotation3(psi: float, theta: float, phi: float) -> np.ndarray:
    """Compute the 3x3 rotation matrix using Euler angles (psi, theta, phi)
phi).

    This function calculates the rotation matrix R by means of matrix multi
multiplication
    of three single matrices that each represent the elementary rotation
    around an axis (X, Y, Z or 1,2,3). The rotation matrix is calculated as
as
    R = Z(phi)*Y(theta)*Z(psi).
    """
    R_psi = np.array([
        [np.cos(psi), -np.sin(psi), 0],
        [np.sin(psi),  np.cos(psi), 0],
        [0, 0, 1]
    ])
    R_theta = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])
    R_phi = np.array([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi),  np.cos(phi), 0],
        [0, 0, 1]
    ])
    R = R_phi @ R_theta @ R_psi
    return R


# src/coilSense/nonCart/bmCoilSense_nonCart_dataFromTwix.py
import numpy as np
from typing import Any, Tuple

def bmCoilSense_nonCart_dataFromTwix(
    argFile: str,
    N_u: Any,
    N: int,
    nSeg: int,
    nShot: int,
    nCh: int,
    FoV: Any,
    nShotOff: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Minimal stub implementation of MATLAB's bmCoilSense_nonCart_dataFromTwi
bmCoilSense_nonCart_dataFromTwix.

    Parameters
    ----------
    argFile : str
        Path to the Twix file.
    N_u : Any
        Size of the grid for every dimension.
    N : int
        Number of points per segment.
    nSeg : int
        Number of segments per shot.
    nShot : int
        Number of shots per acquisition.
    nCh : int
        Number of channels / coils.
    FoV : Any
        Field-of-view values.
    nShotOff : int
        Number of shots to discard from the start.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        Dummy outputs: empty k-space data array, empty trajectory array,
        and empty volume-element array.  The shapes follow the MATLAB
        contract: ``y`` : (0, nCh), ``t`` : (3, 0), ``ve`` : (1, 0).
    """
    # Return empty arrays with appropriate shapes; no heavy computation.
    y = np.empty((0, nCh), dtype=float)
    t = np.empty((3, 0), dtype=float)
    ve = np.empty((1, 0), dtype=float)
    return y, t, ve
