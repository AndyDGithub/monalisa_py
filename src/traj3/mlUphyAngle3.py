import numpy as np
from src.arrayUtility import bmBlockReshape

def mlUphyAngle3(nseg, nshot, varargin):
    # [theta, phi] = mlUphyAngle3(nseg, nshot, varargin)
    #
    # Calculates spherical coordinates for all points (nseg * nshot) of the
    # uniform phyllotaxis spiral UPhy. This spiral covers the north hemisphere only.
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

    goldNum = (1 + np.sqrt(5))/2
    goldAngle = 2*np.pi - (2*np.pi / goldNum)
    flagSelfNav = 0

    if len(varargin) > 0:
        flagSelfNav = varargin[0]

    nseg_tot = nseg * nshot
    if flagSelfNav:
        nseg_pure = nseg_tot - nshot
    else:
        nseg_pure = nseg_tot

    q = np.pi/2
    phi = np.zeros(1, nseg_tot)
    theta = np.zeros(1, nseg_tot)
    myCounter = 1

    for i in range(nseg):
        for j in range(nshot):
            myIndex = i + (j-1) * nseg
            if flagSelfNav and i == 0:
                phi[myIndex] = 0
                theta[myIndex] = 0
            else:
                phi[myIndex] = np.mod(myCounter*goldAngle, 2*np.pi)
                theta[myIndex] = q * np.arccos(1 - myCounter/nseg_pure)
                myCounter += 1

    return theta, phi
