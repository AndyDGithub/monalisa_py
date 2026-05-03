from __future__ import annotations

from third_part.matlab_compat.matlab_native import isempty

import numpy as np


def bmVarargin_RMS_flag(myRMS_flag):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    if isempty(myRMS_flag):
        return True
    else:
        return myRMS_flag
