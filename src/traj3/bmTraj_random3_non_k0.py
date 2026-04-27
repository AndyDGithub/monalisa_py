from __future__ import annotations
from third_part.matlab_compat.matlab_native import double, size


def bmTraj_random3_non_k0(nPt, N_u, dK_u):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: myEps = 100*eps; % -------------------------------------------------------- magic_number
    # MATLAB: N_u     = double(N_u(:)');
    # MATLAB: dK_u    = double(dK_u(:)');
    # MATLAB: lx = (N_u(1, 1)-1)*dK_u(1, 1);
    # MATLAB: ly = (N_u(1, 2)-1)*dK_u(1, 2);
    # MATLAB: lz = (N_u(1, 3)-1)*dK_u(1, 3);
    # MATLAB: sx = N_u(1, 1)/2*dK_u(1, 1);
    # MATLAB: sy = N_u(1, 2)/2*dK_u(1, 2);
    # MATLAB: sz = N_u(1, 3)/2*dK_u(1, 3);
    # MATLAB: x = (rand(1, nPt)*lx) - sx;
    # MATLAB: y = (rand(1, nPt)*ly) - sy;
    # MATLAB: z = (rand(1, nPt)*lz) - sz;
    # MATLAB: t = cat(1, x(:)', y(:)', z(:)');
    # MATLAB: n = sqrt( t(1, :).^2 + t(2, :).^2 + t(3, :).^2 );
    # MATLAB: m = (n < myEps);
    # MATLAB: t(:, m(:)') = [];
    # MATLAB: nPt_miss = nPt - size(t, 2);
    # MATLAB: for i = 1:nPt_miss
    # MATLAB: x = rand*lx - sx;
    # MATLAB: y = rand*ly - sy;
    # MATLAB: z = rand*lz - sz;
    # MATLAB: n = sqrt(x^2 + y^2 + z^2);
    # MATLAB: while (n < myEps)
    # MATLAB: x = rand*lx - sx;
    # MATLAB: y = rand*ly - sy;
    # MATLAB: z = rand*lz - sz;
    # MATLAB: n = sqrt(x^2 + y^2 + z^2);
    # MATLAB: end
    # MATLAB: t = cat(2, [x, y, z]', t);
    # MATLAB: end
    # MATLAB: if size(t, 2) ~= nPt
    # MATLAB: error('The output traj has wrong size. ');
    # MATLAB: return;
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    t = None
    return t
