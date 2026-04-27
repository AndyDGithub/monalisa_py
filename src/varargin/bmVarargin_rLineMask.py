from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty


def bmVarargin_rLineMask(inMask, nLine):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if not(isempty(inMask))
    # MATLAB: outMask = inMask;
    # MATLAB: else
    # MATLAB: outMask = true(1, nLine);
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    outMask = None
    return outMask
