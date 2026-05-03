from __future__ import annotations
import numpy as np
from src.traj3.mlUphyAngle3 import mlUphyAngle3


def mlTraj_fullRadial3_phyllotaxis_uniform_lineAssym2(varargin):
    """Create a uniform phyllotaxis (uphy) 3D radial trajectory.

    Authors:
    Mauro Leidi
    HES-SO
    Lausanne - Switzerland
    May 2025

    Parameters:
    varargin: Either a single bmMriAcquisitionParam object or 6 separate
              values:
        N_n (int): Number of points per line.
        nSeg (int): Number of segments per shot.
        nShot (int): Number of shots.
        dK_n (float): K-space step size (1/FoV).
        flagSelfNav (bool): First segment of each shot is at the top of the
                            sphere if True.
        nShot_off (int): Number of initial shots to discard.

    Returns:
    myTraj (array): Trajectory of shape [3, N_n, M], where
                    M = (nShot - nShot_off) * (nSeg - flagSelfNav).
    """
    if varargin is None or len(varargin) == 0:
        raise ValueError('Wrong list of arguments.')
    elif len(varargin) == 1:
        p           = varargin[0]
        N_n         = int(p.N)
        nSeg        = int(p.nSeg)
        nShot       = int(p.nShot)
        dK_n        = 1.0 / float(np.mean(np.asarray(p.FoV).ravel()))
        flagSelfNav = bool(p.selfNav_flag)
        nShot_off   = int(p.nShot_off)
    elif len(varargin) == 6:
        N_n         = int(varargin[0])
        nSeg        = int(varargin[1])
        nShot       = int(varargin[2])
        dK_n        = float(varargin[3])
        flagSelfNav = bool(varargin[4])
        nShot_off   = int(varargin[5])
    else:
        raise ValueError('Wrong list of arguments.')

    if N_n % 2 != 0:
        raise ValueError('N_n must be even in mlTraj_fullRadial3_phyllotaxis_uniform_lineAssym2!')

    # Compute spherical angles for the phyllotaxis spiral
    theta, phi = mlUphyAngle3(nSeg, nShot, flagSelfNav)
    # theta and phi are each of length nSeg * nShot

    # Radial samples: N_n points from -0.5 to 0.5 (exclusive)
    r = np.arange(-0.5, 0.5 - 1.0 / N_n + 1e-12, 1.0 / N_n)  # length N_n

    n_lines  = nSeg * nShot
    phi_flat   = phi.ravel()    # (n_lines,)
    theta_flat = theta.ravel()  # (n_lines,)

    # Broadcast to (N_n, n_lines)
    phi_2d   = np.tile(phi_flat,   (N_n, 1))          # (N_n, n_lines)
    theta_2d = np.tile(theta_flat, (N_n, 1))          # (N_n, n_lines)
    R_2d     = np.tile(r.reshape(-1, 1), (1, n_lines)) # (N_n, n_lines)

    # Convert spherical to Cartesian coordinates
    x = R_2d * np.cos(phi_2d) * np.sin(theta_2d)  # (N_n, n_lines)
    y = R_2d * np.sin(phi_2d) * np.sin(theta_2d)
    z = R_2d * np.cos(theta_2d)

    # Reshape to (N_n, nSeg, nShot)
    x = x.reshape(N_n, nSeg, nShot)
    y = y.reshape(N_n, nSeg, nShot)
    z = z.reshape(N_n, nSeg, nShot)

    # Stack and scale: shape (3, N_n, nSeg, nShot)
    myTraj = np.stack([x, y, z], axis=0) * N_n * dK_n

    # Remove self-navigator segment (first segment of each shot)
    if flagSelfNav:
        myTraj = myTraj[:, :, 1:, :]  # remove segment index 0

    # Remove leading discarded shots
    if nShot_off > 0:
        myTraj = myTraj[:, :, :, nShot_off:]

    # Reshape to (3, N_n, nSeg_remaining * nShot_remaining)
    s = myTraj.shape
    myTraj = myTraj.reshape(3, s[1], s[2] * s[3])

    return myTraj
