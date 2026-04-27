from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty


def bmVarargin_RMS_flag(myRMS_flag):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if isempty(myRMS_flag)
    # MATLAB: out = true;
    # MATLAB: else
    # MATLAB: out = myRMS_flag;
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out = None
    return out
