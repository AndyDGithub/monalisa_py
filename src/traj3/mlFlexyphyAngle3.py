import numpy as np
from src.arrayUtility import bmBlockReshape  # Import the required function from arrayUtility module

def mlFlexyphyAngle3(nseg, nshot, varargin):
    # [theta, phi] = mlFlexyphyAngle3(nseg, nshot, varargin)
    #
    # Calculates spherical coordinates for all points (nseg * nshot) of the
    # flexyphy spiral. This spiral covers the north hemisphere only (For each redout it only computes the most external point)
    # The radius r is constant and not defined by this function.
    #
    # Authors:
    # Mauro Leidi
    # HES-SO
    # Lausanne - Switzerland
    # May 2025
    #
    # Parameters:
    # nseg (int): Number of segments per shot
    # nshot (int): Number of shots of the acquisition
    # varargin (bool, optional): Flag if the first segment acquired is the same for all shots (self navigation). Default value is 0.
    #
    # Returns:
    # theta (array): List containing the polar angle for every point of the spiral
    # phi (array): List containing the azimuthal angle for every point of the spiral

    flagSelfNav = 0
    if len(varargin) > 0:
        flagSelfNav = varargin[0]
    
    rng(1, "twister")  # Set the seed for reproducibility and it should be the same as the one used in acquisition
    shuffling = np.random.permutation(nshot)  # Randomly shuffle the list

    nseg_tot = nshot * nseg  # = shot x segments
    phi = np.zeros(nseg_tot)
    theta = np.zeros(nseg_tot)
    x = np.zeros(nseg_tot)
    y = np.zeros(nseg_tot)
    z = np.zeros(nseg_tot)

    N = nseg_tot - nshot if flagSelfNav else nseg_tot
    Gn = (1 + np.sqrt(5)) / 2
    Gn_ang = 2 * np.pi - (2 * np.pi / Gn)
    count = 1

    for seg in range(1, nseg + 1):
        for shot in range(nshot):
            myIndex = seg + (shot - 1) * nseg

            if flagSelfNav and seg == 1:
                theta[myIndex] = 0
                phi[myIndex] = 0
            else:
                count2 = shuffling[shot] + (seg - 2) * nshot
                theta[myIndex] = np.arccos(1 - count2 / N)
                phi[myIndex] = np.mod((count * Gn_ang), (2 * np.pi))

            count += 1
            # x[myIndex] = np.sin(theta[myIndex]) * np.cos(phi[myIndex])
            # y[myIndex] = np.sin(theta[myIndex]) * np.sin(phi[myIndex])
            # z[myIndex] = np.cos(theta[myIndex])

    return theta, phi
