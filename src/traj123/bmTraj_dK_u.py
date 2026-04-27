"""
bmTraj_dK_u
~~~~~~~~~~~

Compute the k-space spacing `dK` from a trajectory `t`.

The original MATLAB implementation was converted to plain Python
without relying on NumPy.  Only the helper functions
`bmTraj_N_u`, `bmTraj_nLine` and `bmPointReshape` are imported from
the project package as required.

This module is intentionally lightweight so that it imports
cleanly in the test environment.  All calculations are performed
with built-in functions, and a simple median routine is implemented
for the 2-D / 3-D refinement step.
"""

# Import helper functions that are guaranteed to exist in the test
# environment.  They are part of the project package and do not
# depend on external libraries such as NumPy.
from src.traj123.bmTraj_N_u import bmTraj_N_u
from src.traj123.bmTraj_nLine import bmTraj_nLine
from src.arrayUtility.bmPointReshape import bmPointReshape

# --------------------------------------------------------------------
def _median(values):
    """
    Return the median of a list of numeric values.

    The implementation is compatible with both odd and even lengths
    (for even lengths it returns the average of the two middle values).
    """
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 0:
        return None
    mid = n // 2
    if n % 2:
        return sorted_vals[mid]
    else:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0

# --------------------------------------------------------------------
def bmTraj_dK_u(t, varargin=None):
    """
    Compute the k-space spacing dK from a trajectory ``t``.

    Parameters
    ----------
    t : array_like
        The trajectory.  Rows correspond to spatial dimensions and
        columns to trajectory points.
    varargin : list, optional
        Optional list of parameters.  The first element, if present,
        specifies the number of samples ``N_u``.

    Returns
    -------
    list
        A single-element list containing the computed dK value(s).  For
        1-D the list contains one float, for 2-D it contains a tuple of
        two floats, and for 3-D it contains a tuple of three floats.

    Notes
    -----
    The algorithm mirrors the MATLAB reference but uses only
    standard Python.  It performs a simple refinement step for 2-D
    and 3-D trajectories based on the median of line distances.
    """
    # Handle optional arguments
    if varargin is None:
        varargin = []

    N_u = None
    if len(varargin) > 0:
        # Convert to a flat list of floats
        N_u = [float(v) for v in varargin[0]]
    if N_u is None or len(N_u) == 0:
        # Call the helper to compute N_u if not supplied
        N_u = bmTraj_N_u(t)
    # Ensure N_u is a list of floats
    N_u = [float(v) for v in N_u]

    # Reshape the trajectory consistently
    t = bmPointReshape(t)
    imDim = len(t)  # number of spatial dimensions

    # Validate input
    if imDim == 0 or len(t[0]) == 0:
        raise ValueError("Input trajectory is empty.")

    # Compute basic dK values along each dimension
    dK = [None] * imDim
    for i in range(imDim):
        dim_vals = [float(v) for v in t[i]]
        dim_min, dim_max = min(dim_vals), max(dim_vals)
        samples = N_u[i] if i < len(N_u) else 0
        dK[i] = abs(dim_max - dim_min) / (samples - 1) if samples > 1 else 0.0

    # --------------------------------------------------------------------
    # Refinement step for 2-D and 3-D trajectories
    # ---------------------------------------------------------------
    if imDim == 2 and dK[0] is not None and dK[1] is not None:
        if abs(dK[0] - dK[1]) / max(dK[0], dK[1]) < 0.02:
            # Get line distances
            _, _, _, dK_n = bmTraj_nLine(t)
            # Filter out outliers
            med = _median(dK_n)
            dK_n = [x for x in dK_n if 0.5 * med <= x <= 2 * med]
            med = _median(dK_n) if dK_n else med
            dK[0] = dK[1] = med

    if imDim == 3:
        # Compute relative differences
        d1 = abs(dK[0] - dK[1]) / max(dK[0], dK[1]) if dK[0] and dK[1] else 0.0
        d2 = abs(dK[1] - dK[2]) / max(dK[1], dK[2]) if dK[1] and dK[2] else 0.0
        d3 = abs(dK[2] - dK[0]) / max(dK[2], dK[0]) if dK[2] and dK[0] else 0.0
        if max(d1, d2, d3) < 0.02:
            _, _, _, dK_n = bmTraj_nLine(t)
            med = _median(dK_n)
            dK_n = [x for x in dK_n if 0.5 * med <= x <= 2 * med]
            med = _median(dK_n) if dK_n else med
            dK = [med] * 3

    # --------------------------------------------------------------------
    # Return a MATLAB-style single-element list
    # ---------------------------------------------------------------
    if imDim == 1:
        return [dK[0]]
    elif imDim == 2:
        return [tuple(dK)]
    elif imDim == 3:
        return [tuple(dK)]
    else:
        return []

# --------------------------------------------------------------------
# End of bmTraj_dK_u
# --------------------------------------------------------------------
