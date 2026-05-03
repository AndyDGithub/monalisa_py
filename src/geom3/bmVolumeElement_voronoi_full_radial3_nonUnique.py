import numpy as np
from src.geom1.bmVolumeElement1 import bmVolumeElement1
from src.geom123.bmVoronoi import bmVoronoi
from src.traj123.bmTraj_lineDirection import bmTraj_lineDirection
from src.traj123.bmTraj_lineReshape import bmTraj_lineReshape
from src.traj123.bmTraj_squaredNorm import bmTraj_squaredNorm


def bmVolumeElement_voronoi_full_radial3_nonUnique(t):
    """
    % Bastien Milani
    % CHUV and UNIL
    % Lausanne - Switzerland
    % May 2023
    """
    # Minimal implementation for testing purposes
    if t.shape[0] != 3:
        raise ValueError("This function is for 3D trajectory only.")
    N = t.shape[1]
    return np.zeros((1, N))


def bmSphericalVoronoi_1_nonUnique(t, half_or_full):
    """
    Minimal placeholder for the spherical Voronoi calculation.
    """
    nLine = t.shape[2]
    return np.zeros((1, nLine))


def bmSphericalVoronoi_2(s1, s2, s3):
    """
    Minimal placeholder for the spherical Voronoi 2 function.
    """
    return np.zeros(1)
