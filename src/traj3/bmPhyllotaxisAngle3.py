import numpy as np


def bmPhyllotaxisAngle3(nseg, nshot, flagSelfNav=False):
    """
    Compute spherical coordinates for all points of the phyllotaxis spiral.

    Port of MATLAB bmPhyllotaxisAngle3.m.

    Parameters
    ----------
    nseg : int
        Number of segments per shot.
    nshot : int
        Number of shots.
    flagSelfNav : bool, optional
        If True the first segment of each shot is fixed at the top of the
        sphere (self-navigation).  Default False.

    Returns
    -------
    theta : ndarray, shape (1, nseg*nshot)
        Polar angles.
    phi : ndarray, shape (1, nseg*nshot)
        Azimuthal angles.
    """
    goldNum = (1.0 + np.sqrt(5.0)) / 2.0
    goldAngle = 2.0 * np.pi - 2.0 * np.pi / goldNum

    nseg_tot = nseg * nshot
    nseg_pure = nseg_tot - nshot if flagSelfNav else nseg_tot

    q = np.pi / (2.0 * np.sqrt(float(nseg_pure)))

    phi = np.zeros((1, nseg_tot), dtype=np.float64)
    theta = np.zeros((1, nseg_tot), dtype=np.float64)

    myCounter = 1

    for i in range(1, nseg + 1):
        for j in range(1, nshot + 1):
            myIndex = i + (j - 1) * nseg   # 1-based MATLAB index
            if flagSelfNav and (i == 1):
                phi[0, myIndex - 1] = 0.0
                theta[0, myIndex - 1] = 0.0
            else:
                phi[0, myIndex - 1] = np.mod(myCounter * goldAngle, 2.0 * np.pi)
                theta[0, myIndex - 1] = q * np.sqrt(float(myCounter))
                myCounter += 1

    return theta, phi
