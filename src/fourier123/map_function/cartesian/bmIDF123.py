from __future__ import annotations
from third_part.matlab_compat.matlab_native import size


def bmIDF123(x, N_u, dK_u):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if size(N_u(:), 1) == 1
    # MATLAB: iF = bmIDF1(x, N_u, dK_u);
    # MATLAB: elseif size(N_u(:), 1) == 2
    # MATLAB: iF = bmIDF2(x, N_u, dK_u);
    # MATLAB: elseif size(N_u(:), 1) == 3
    # MATLAB: iF = bmIDF3(x, N_u, dK_u);
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    iF = None
    return iF
