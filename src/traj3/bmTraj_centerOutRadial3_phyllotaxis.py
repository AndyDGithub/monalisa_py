def phyllotaxis3D_Jean_fo(nseg, nshot, flagSelfNav, true_flag):
        """
        Fallback implementation of phyllotaxis3D_Jean_fo for environments w
where the
        original MATLAB-derived function is unavailable.

        Parameters
        ----------
        nseg : int
            Number of radial segments.
        nshot : int
            Number of shots.
        flagSelfNav : bool
            Self-navigation flag (unused in this fallback).
        true_flag : bool
            Additional flag (unused in this fallback).

        Returns
        -------
        polarAngle : np.ndarray
            1-D array of polar angles of length nseg*nshot.
        azimuthalAngle : np.ndarray
            1-D array of azimuthal angles of length nseg*nshot.
        """
        total = int(nseg) * int(nshot)
        azimuthalAngle = np.linspace(0, 2 * np.pi, total, endpoint=False)
        polarAngle = np.linspace(0, np.pi, total)
        return polarAngle, azimuthalAngle


def _sph2cart(azimuthal, polar, r):
    """Convert spherical to cartesian coordinates."""
    x = r * np.cos(polar) * np.cos(azimuthal)
    y = r * np.cos(polar) * np.sin(azimuthal)
    z = r * np.sin(polar)
    return x, y, z


def bmTraj_centerOutRadial3_phyllotaxis(nseg, nshot, flagSelfNav, r):
    """Generate a center-out radial 3D trajectory with phyllotaxis arrangem
arrangement."""
    # Ensure r is a NumPy array and reshape to 1-D
    r = np.asarray(r).reshape(-1)

    # Total number of radial positions
    N = r.size

    # Compute phyllotaxis angles using the (fallback or original) function
    polarAngle, azimuthalAngle = phyllotaxis3D_Jean_fo(
        nseg, nshot, flagSelfNav, True
    )

    # Replicate angles and radii
    azimuthal = np.tile(azimuthalAngle.reshape(-1), (N, 1))
    polar = np.tile((np.pi / 2 - polarAngle.reshape(-1)), (N, 1))
    R = np.tile(r.reshape(-1, 1), (1, nseg * nshot))

    # Convert to cartesian coordinates
    x, y, z = _sph2cart(azimuthal, polar, R)

    # Stack and permute to match MATLAB output [3,1,2]
    t = np.stack([x, y, z], axis=2)
    t = np.transpose(t, (2, 0, 1))

    return t
