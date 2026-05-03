from __future__ import annotations
import numpy as np
from src.fourier1.bmDFT1_conjTrans import bmDFT1_conjTrans
from src.fourier2.bmDFT2_conjTrans import bmDFT2_conjTrans
from src.fourier3.bmDFT3_conjTrans import bmDFT3_conjTrans
from src.geom123 import bmTraj

from third_part.matlab_compat.matlab_native import size

def bmDFT123_conjTrans(x, N_u, dK_u):
    """Strict deterministic baseline port from MATLAB."""
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    if size(N_u, 1) == 1:
        starF = bmDFT1_conjTrans(x, N_u, dK_u)
    elif size(N_u, 1) == 2:
        starF = bmDFT2_conjTrans(x, N_u, dK_u)
    elif size(N_u, 1) == 3:
        starF = bmDFT3_conjTrans(x, N_u, dK_u)
    return starF
