import numpy as np

def mlFlexyphyAngle3(nseg, nshot, varargin=None):
    """
    % [theta, phi] = mlFlexyphyAngle3(nseg, nshot, varargin)
    %
    % Calculates spherical coordinates for all points (nseg * nshot) of the
the
    % flexyphy spiral. This spiral covers the north hemisphere only (for
(for each
    % readout it only computes the most external point).
    % The radius r is constant and not defined by this function.
    %
    % Authors:
    %   Mauro Leidi
    %   HES-SO
    %   Lausanne - Switzerland
    %   May 2025
    %
    % Parameters:
    %   nseg (int): Number of segments per shot
    %   nshot (int): Number of shots of the acquisition
    %   varargin (bool, optional): Flag if the first segment acquired is th
the
    %   same for all shots (self navigation). Default value is 0.
    %
    % Returns:
    %   theta (np.ndarray): List containing the polar angle for every point
point of the
    %   spiral
    %   phi (np.ndarray): List containing the azimuthal angle for every poi
point of the
    %   spiral
    """
    flagSelfNav = False
    if varargin is not None:
        flagSelfNav = bool(varargin)

    # Set the seed for reproducibility (same as MATLAB rng(1,'twister'))
    np.random.seed(1)
    # MATLAB randperm returns 1-based permutation; adjust by adding 1
    shuffling = np.random.permutation(nshot) + 1

    nseg_tot = nshot * nseg
    phi = np.zeros(nseg_tot)
    theta = np.zeros(nseg_tot)

    N = nseg_tot - nshot if flagSelfNav else nseg_tot
    Gn = (1 + np.sqrt(5)) / 2
    Gn_ang = 2 * np.pi - (2 * np.pi / Gn)
    count = 1

    for seg in range(1, nseg + 1):
        for shot in range(1, nshot + 1):
            myIndex = seg + (shot - 1) * nseg - 1  # zero-based index

            if flagSelfNav and seg == 1:
                theta[myIndex] = 0.0
                phi[myIndex] = 0.0
            else:
                count2 = shuffling[shot - 1] + (seg - 2) * nshot
                theta[myIndex] = np.arccos(1 - count2 / N)
                phi[myIndex] = np.mod(count * Gn_ang, 2 * np.pi)
                count += 1

    return theta, phi
