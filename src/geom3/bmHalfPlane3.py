from __future__ import annotations
from third_part.matlab_compat.matlab_native import repmat, size


def bmHalfPlane3(argPlane, N_u):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: N_u = N_u(:)';
    # MATLAB: p = argPlane.p;
    # MATLAB: n = argPlane.n;
    # MATLAB: [X, Y, Z] = ndgrid(1:N_u(1, 1), 1:N_u(1, 2), 1:N_u(1, 3));
    # MATLAB: x = cat(1, X(:)', Y(:)', Z(:)');
    # MATLAB: p = repmat(p(:), [1, size(x, 2)]);
    # MATLAB: x = x - p;
    # MATLAB: m = reshape(sign(n'*x) > 0, N_u);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    m = None
    return m
