import numpy as np
from scipy.interpolate import interp1d

def bmLengthParamPath(p, length_between_neighbors):
    nPt = np.shape(p, 2)
    L = length_between_neighbors
    t = np.linspace(0, 1, nPt)
    tq = np.linspace(0, 1, nPt*1000)  # --------------------------------------------- magic_number

    interp_x = interp1d(t, p[:, 0], kind='pchip')(tq)
    interp_y = interp1d(t, p[:, 1], kind='pchip')(tq)
    interp_z = interp1d(t, p[:, 2], kind='pchip')(tq)

    p_interp = np.column_stack((interp_x, interp_y, interp_z))
    nPt_interp = np.shape(p_interp, 1)
    L_curr = 0
    p_out = np.array([p_interp[0, :]])

    for i in range(1, nPt_interp):
        p2 = p_interp[:, i]
        L_curr += np.linalg.norm(p2 - p_interp[:, i-1])

        if L_curr >= L:
            p1 = (p_interp[:, i-1] + p2) / 2
            p_out = np.vstack((p_out, p1))
            L_curr = 0
        else:
            p1 = p2

    if not np.allclose(p_out[:, -1], p[:, -1]):
        p_out = np.vstack((p_out, p[:, -1]))

    return p_out
