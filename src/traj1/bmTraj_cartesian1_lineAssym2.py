import numpy as np

def bmTraj_cartesian1_lineAssym2(*varargin):
    """
    Construct a 1-D Cartesian trajectory line with optional asymmetry.
    
    Parameters
    ----------
    *varargin : tuple
        Either a single object with attributes `N_u` and `dK_u` (e.g. a
        `bmTrajInfo` instance), or two arrays/lists `N_u` and `dK_u`.
    
    Returns
    -------
    np.ndarray
        The trajectory samples.
    """
    if len(varargin) == 0:
        raise TypeError("bmTraj_cartesian1_lineAssym2 requires at least one argument")

    # Determine if the first argument contains N_u and dK_u attributes
    first = varargin[0]
    if hasattr(first, "N_u") and hasattr(first, "dK_u"):
        t_info = first
        N_u = t_info.N_u
        dK_u = t_info.dK_u
    else:
        if len(varargin) < 2:
            raise TypeError("bmTraj_cartesian1_lineAssym2 requires two arguments if not given a bmTrajInfo object")
        N_u = varargin[0]
        dK_u = varargin[1]

    # Ensure we work with 1-D arrays
    N_u = np.asarray(N_u).reshape(-1)
    dK_u = np.asarray(dK_u).reshape(-1)

    # Construct the trajectory
    x = np.arange(-N_u[0] / 2.0, N_u[0] / 2.0) * dK_u[0]
    return x.reshape(-1)
