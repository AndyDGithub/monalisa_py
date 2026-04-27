from __future__ import annotations
from third_part.matlab_compat.matlab_native import size


def bmDFT123_conjTrans(x, N_u, dK_u):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if size(N_u(:), 1) == 1
    # MATLAB: starF = bmDFT1_conjTrans(x, N_u, dK_u);
    # MATLAB: elseif size(N_u(:), 1) == 2
    # MATLAB: starF = bmDFT2_conjTrans(x, N_u, dK_u);
    # MATLAB: elseif size(N_u(:), 1) == 3
    # MATLAB: starF = bmDFT3_conjTrans(x, N_u, dK_u);
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    starF = None
    return starF
