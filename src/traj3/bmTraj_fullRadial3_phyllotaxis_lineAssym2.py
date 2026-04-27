import numpy as np
from src.traj3.bmPhyllotaxisAngle3 import bmPhyllotaxisAngle3


def bmTraj_fullRadial3_phyllotaxis_lineAssym2(arg):
    """
    Compute a 3-D full-radial phyllotaxis trajectory.

    Port of MATLAB bmTraj_fullRadial3_phyllotaxis_lineAssym2.m.

    Parameters
    ----------
    arg : bmMriAcquisitionParam or tuple of 6 values
        If an acquisition-param object: reads N, nSeg, nShot, FoV, selfNav_flag,
        nShot_off (and optionally flagExcludeSI).
        If a tuple: (N_n, nSeg, nShot, dK_n, flagSelfNav, nShot_off).

    Returns
    -------
    myTraj : ndarray, shape (3, N_n, nLines)
        Normalised k-space trajectory where
        nLines = (nSeg - flagExcludeSI) * (nShot - nShot_off).
    """
    if isinstance(arg, tuple):
        N_n, nSeg, nShot, dK_n, flagSelfNav, nShot_off = arg
        flagExcludeSI = flagSelfNav
    else:
        p = arg
        N_n = int(p.N)
        nSeg = int(p.nSeg)
        nShot = int(p.nShot)
        dK_n = 1.0 / float(np.mean(np.asarray(p.FoV).ravel()))
        flagSelfNav = bool(p.selfNav_flag)
        flagExcludeSI = bool(getattr(p, 'flagExcludeSI', p.selfNav_flag))
        nShot_off = int(p.nShot_off)

    if N_n % 2 != 0:
        raise ValueError("N_n must be even in bmTraj_fullRadial3_phyllotaxis_lineAssym2!")

    # Spherical angles: theta, phi each (1, nSeg*nShot)
    theta, phi = bmPhyllotaxisAngle3(nSeg, nShot, flagSelfNav)
    theta = theta.ravel()   # (nSeg*nShot,)
    phi = phi.ravel()

    # Radial positions along each line: N_n points from -0.5 to 0.5-1/N_n
    r = np.arange(-0.5, 0.5, 1.0 / N_n, dtype=np.float64)  # (N_n,)

    # Reshape theta/phi to (nSeg, nShot) in MATLAB column-major (Fortran) order:
    #   theta_2d[s, j] = theta[s + j*nSeg]  (s=seg 0-based, j=shot 0-based)
    theta_2d = theta.reshape(nSeg, nShot, order='F')  # (nSeg, nShot)
    phi_2d = phi.reshape(nSeg, nShot, order='F')

    # Build (N_n, nSeg, nShot) coordinate arrays
    r3 = r[:, np.newaxis, np.newaxis]          # (N_n, 1, 1)
    cos_phi = np.cos(phi_2d)[np.newaxis]       # (1, nSeg, nShot)
    sin_phi = np.sin(phi_2d)[np.newaxis]
    cos_theta = np.cos(theta_2d)[np.newaxis]
    sin_theta = np.sin(theta_2d)[np.newaxis]

    x_3d = r3 * cos_phi * sin_theta            # (N_n, nSeg, nShot)
    y_3d = r3 * sin_phi * sin_theta
    z_3d = r3 * cos_theta

    # (3, N_n, nSeg, nShot), scaled
    myTraj = np.stack([x_3d, y_3d, z_3d], axis=0) * N_n * dK_n

    # Remove SI projection (first segment) if flagExcludeSI
    if flagExcludeSI:
        myTraj = myTraj[:, :, 1:, :]    # (3, N_n, nSeg-1, nShot)

    # Remove non-steady-state shots
    if nShot_off > 0:
        myTraj = myTraj[:, :, :, nShot_off:]   # (3, N_n, nSeg_act, nShot_act)

    # Flatten last two dims: (3, N_n, nLines) in Fortran order to match MATLAB
    # MATLAB col-major: line k = segment s + shot j * nSeg_act (k = s + j*nSeg_act)
    nSeg_act = myTraj.shape[2]
    nShot_act = myTraj.shape[3]
    myTraj = myTraj.reshape(3, N_n, nSeg_act * nShot_act, order='F')

    return myTraj
