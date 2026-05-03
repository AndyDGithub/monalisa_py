import numpy as np

def bmPhyllotaxisAngle3(nseg, nshot, flagSelfNav=False):
    """
    Compute spherical coordinates for all points of the phyllotaxis spiral.
spiral.
    
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

    # Define golden angle 
    goldNum     = (1 + np.sqrt(5)) / 2
    goldAngle   = 2 * np.pi - (2 * np.pi / goldNum)

    # Define total number of points / segments
    nseg_tot = nseg * nshot
    if flagSelfNav:
        nseg_pure = nseg_tot - nshot
    else:
        nseg_pure = nseg_tot

    # Ratio for polar angle theta
    q = np.pi / (2 * np.sqrt(nseg_pure)) 

    # Set up arrays
    phi     = np.zeros((1, nseg_tot))
    theta   = np.zeros((1, nseg_tot))

    # Angle index, differs from myIndex if flagSelfNav = true
    myCounter = 1

    # Calculate spiral
    for i in range(1, nseg + 1):
        for j in range(1, nshot + 1):
            # MATLAB: myIndex = i + (j-1) * nseg (1-based).
            myIndex = (i - 1) + (j - 1) * nseg
            # Set angles to 0 if flagSelfNav = true (top of sphere)
            if flagSelfNav and (i == 1):
                phi[0, myIndex] = 0.0
                theta[0, myIndex] = 0.0
            else:
                # Calculate angle for each segment
                phi[0, myIndex] = np.mod(myCounter * goldAngle, (2 * np.pi))
                theta[0, myIndex] = q * np.sqrt(myCounter)
                myCounter += 1

    return theta, phi
