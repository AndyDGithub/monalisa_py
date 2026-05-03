from __future__ import annotations

from third_part.matlab_compat.matlab_native import isempty

def bmVarargin_rLineMask(inMask, nLine):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    if not(isempty(inMask)):
        outMask = inMask 
    else:
        outMask = np.ones((1, nLine), dtype=bool) 
    return outMask
