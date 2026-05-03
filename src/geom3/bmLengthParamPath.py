import numpy as np
from scipy.interpolate import pchip_interpolate

def bmLengthParamPath(p, length_between_neighbors):
    """
    Compute a path with equal segment lengths based on the input points.

    Parameters
    ----------
    p : array_like
        3xN array of points (x, y, z). If the input has shape (N, 3) it is
        automatically transposed.
    length_between_neighbors : float
        Desired distance between successive points in the output path.

    Returns
    -------
    p_out : ndarray
        3xM array of points with approximately uniform spacing of
        `length_between_neighbors`. The first and last input points are
        preserved.
    """
    # Ensure input is a NumPy array
    p_arr = np.asarray(p, dtype=float)

    # Accept both 3xN and Nx3 conventions
    if p_arr.shape[0] == 3:
        points = p_arr
    elif p_arr.shape[1] == 3:
        points = p_arr.T
    else:
        raise ValueError("Input array must be of shape (3, N) or (N, 3)")

    n_pt = points.shape[1]
    L = float(length_between_neighbors)

    t = np.linspace(0.0, 1.0, n_pt)
    tq = np.linspace(0.0, 1.0, n_pt * 1000)  # magic_number

    # Interpolate each coordinate with monotonic cubic (pchip)
    interp_x = pchip_interpolate(t, points[0, :], tq)
    interp_y = pchip_interpolate(t, points[1, :], tq)
    interp_z = pchip_interpolate(t, points[2, :], tq)

    # Interpolated points as 3 x N_interp array
    p_interp = np.vstack((interp_x, interp_y, interp_z))
    n_pt_interp = p_interp.shape[1]

    # Build output path
    p_out = [p_interp[:, 0]]
    p1 = p_interp[:, 0]
    L_curr = 0.0

    for i in range(1, n_pt_interp):
        p2 = p_interp[:, i]
        L_curr += np.linalg.norm(p2 - p1)
        if L_curr >= L:
            # Insert mid-point to maintain spacing
            mid_point = (p1 + p2) / 2.0
            p_out.append(mid_point)
            L_curr = 0.0
        else:
            p1 = p2

    # Ensure the last point matches the last original point
    if not np.allclose(p_out[-1], points[:, -1]):
        p_out.append(points[:, -1])

    return np.column_stack(p_out)

# Import bmTraj from src.geom123 module
from src.geom123 import bmTraj
