from __future__ import annotations
from third_part.matlab_compat.matlab_native import repmat


def bmTraj_randomPartialCartesian3_x(N_u, dK_u, myPerOne):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: N_u     = N_u(:)';
    # MATLAB: dK_u    = dK_u(:)';
    # MATLAB: Nx  = N_u(1, 1);
    # MATLAB: Ny  = N_u(1, 2);
    # MATLAB: Nz  = N_u(1, 3);
    # MATLAB: dKx = dK_u(1, 1);
    # MATLAB: dKy = dK_u(1, 2);
    # MATLAB: dKz = dK_u(1, 3);
    # MATLAB: kx = (-Nx/2:Nx/2 - 1)*dKx;
    # MATLAB: ky = (-Ny/2:Ny/2 - 1)*dKy;
    # MATLAB: kz = (-Nz/2:Nz/2 - 1)*dKz;
    # MATLAB: [ky, kz] = ndgrid(ky, kz);
    # MATLAB: ky       = ky(:)';
    # MATLAB: kz       = kz(:)';
    # MATLAB: m = (rand(1, Ny*Nz) <= myPerOne);
    # MATLAB: nLine = sum(m(:));
    # MATLAB: ky = ky(1, m);
    # MATLAB: kz = kz(1, m);
    # MATLAB: kx = repmat(kx(:) , [1, nLine]);
    # MATLAB: ky = repmat(ky(:)', [Nx, 1]);
    # MATLAB: kz = repmat(kz(:)', [Nx, 1]);
    # MATLAB: t = cat(1, kx(:)', ky(:)', kz(:)');
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    t = None
    return t
