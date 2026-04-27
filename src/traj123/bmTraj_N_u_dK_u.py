import warnings
import numpy as np

from src.traj123.bmTraj_N_u import bmTraj_N_u
from src.traj123.bmTraj_dK_u import bmTraj_dK_u
from src.arrayUtility.bmPointReshape import bmPointReshape


def bmTraj_N_u_dK_u(t, N_u=None, dK_u=None):
    """
    Determine Cartesian grid size N_u and step dK_u from trajectory t.

    If N_u or dK_u are None (or empty), they are estimated from the
    trajectory.  The results are rounded to float32 precision to match
    the MATLAB ``double(single(...))`` conversion.

    Parameters
    ----------
    t    : array (imDim, nPt)
    N_u  : array-like or None
    dK_u : array-like or None

    Returns
    -------
    N_u, dK_u : np.ndarray (float64)
    """
    empty_N  = N_u  is None or (hasattr(N_u,  '__len__') and len(N_u)  == 0)
    empty_dK = dK_u is None or (hasattr(dK_u, '__len__') and len(dK_u) == 0)

    if empty_N:
        warnings.warn(
            'N_u is automatically determined. '
            'You probably want to explicitly pass it as argument instead.')
        N_u = bmTraj_N_u(t)

    if empty_dK:
        warnings.warn(
            'dK_u is automatically determined. '
            'You probably want to explicitly pass it as argument instead.')
        dK_u = bmTraj_dK_u(t, N_u)

    N_u  = np.float64(np.float32(np.array(N_u).ravel()))
    dK_u = np.float64(np.float32(np.array(dK_u).ravel()))
    return N_u, dK_u
