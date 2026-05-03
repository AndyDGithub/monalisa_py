import numpy as np

def mlUphyAngle3(nseg, nshot, varargin=None):
    """
    Calculates spherical coordinates for all points (nseg * nshot) of the
    uniform phyllotaxis spiral UPhy. This spiral covers the north hemispher
hemisphere only.
    The radius r is constant and not defined by this function.

    Parameters
    ----------
    nseg : int
        Number of segments per shot.
    nshot : int
        Number of shots of the acquisition.
    varargin : bool, optional
        Flag if the first segment acquired is the same for all shots
        (self navigation). Default value is 0.

    Returns
    -------
    theta : np.ndarray
        Array containing the polar angle for every point of the spiral.
    phi : np.ndarray
        Array containing the azimuthal angle for every point of the spiral.
spiral.
    """
    gold_num = (1 + np.sqrt(5)) / 2
    gold_angle = 2 * np.pi - (2 * np.pi / gold_num)

    flag_self_nav = False if varargin is None else bool(varargin)

    nseg_tot = nseg * nshot
    nseg_pure = nseg_tot - nshot if flag_self_nav else nseg_tot

    q = np.pi / 2
    phi = np.zeros(nseg_tot)
    theta = np.zeros(nseg_tot)

    my_counter = 1

    for j in range(1, nshot + 1):
        for i in range(1, nseg + 1):
            idx = (j - 1) * nseg + (i - 1)
            if flag_self_nav and i == 1:
                phi[idx] = 0.0
                theta[idx] = 0.0
            else:
                phi[idx] = np.mod(my_counter * gold_angle, 2 * np.pi)
                theta[idx] = q * np.arccos(1 - my_counter / nseg_pure)
                my_counter += 1

    return theta, phi
