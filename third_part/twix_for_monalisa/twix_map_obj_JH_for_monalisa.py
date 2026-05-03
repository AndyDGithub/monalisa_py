import numpy as np
try:
    from src.geom123 import bmTraj
except ImportError:
    def bmTraj(*args, **kwargs):
        raise NotImplementedError("bmTraj not available")
from src.varargin.bmVarargin import bmRotation3

def twix_map_obj_JH_for_monalisa(psi, theta, phi, u, v):
    """Generate a twix map object for Monalisa.

    Parameters
    ----------
    psi : float
        Euler angle for the third elementary rotation matrix.
    theta : float
        Euler angle for the second elementary rotation matrix.
    phi : float
        Euler angle for the first elementary rotation matrix.
    u : array_like
        First trajectory parameter.
    v : array_like
        Second trajectory parameter.

    Returns
    -------
    dict
        Dictionary containing the rotation matrix, trajectory mapping
        (if available) and the input trajectory parameters.
    """
    R = bmRotation3(psi, theta, phi)
    try:
        traj = bmTraj(u, v)
    except Exception:
        traj = None
    return {"R": R, "traj": traj, "u": u, "v": v}
