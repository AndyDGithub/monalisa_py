from __future__ import annotations
from third_part.matlab_compat.matlab_native import permute, repmat, size


def bmTraj_centerOutRadial3_phyllotaxis(nseg, nshot, flagSelfNav, r):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: N = size(r(:), 1);
    # MATLAB: [polarAngle, azimuthalAngle] = phyllotaxis3D_Jean_for_monalisa(nseg, nshot, flagSelfNav, true);
    # MATLAB: azimuthal  = repmat(azimuthalAngle(:)',[N 1]);
    # MATLAB: polar      = repmat(pi/2-polarAngle(:)',[N 1]);
    # MATLAB: R          = repmat(r(:),[1 nseg*nshot]);
    # MATLAB: [x,y,z]    = sph2cart(azimuthal,polar,R);
    # MATLAB: t = cat(3, x, y, z);
    # MATLAB: t = permute(t, [3, 1, 2]);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    t = None
    return t
