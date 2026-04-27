from __future__ import annotations
from third_part.matlab_compat.matlab_native import repmat, size


def bmVolumeElement_randomPartialCartesian3_x(t, N_u, dK_u):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: N_u  = N_u(:)';
    # MATLAB: dK_u = dK_u(:)';
    # MATLAB: Nx = N_u(1, 1);
    # MATLAB: Ny = N_u(1, 2);
    # MATLAB: Nz = N_u(1, 3);
    # MATLAB: dKx = dK_u(1, 1);
    # MATLAB: dKy = dK_u(1, 2);
    # MATLAB: dKz = dK_u(1, 3);
    # MATLAB: t = bmPointReshape(t);
    # MATLAB: nPt = size(t, 2);
    # MATLAB: nLine = nPt/Nx;
    # MATLAB: t   = reshape(t, [3, Nx, nLine]);
    # MATLAB: t1  = bmPointReshape(squeeze(t([2, 3], 1, :)));
    # MATLAB: ve  = bmVolumeElement_voronoi_box2(t1, [Ny, Nz], [dKy, dKz]);
    # MATLAB: ve  = repmat(ve(:)', [Nx, 1]);
    # MATLAB: ve  = dKx*ve(:)';
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    ve = None
    return ve
