from __future__ import annotations

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.fourier1.bmIDF1 import bmIDF1
from src.fourier2.bmIDF2 import bmIDF2
from src.fourier3.bmIDF3 import bmIDF3


def bmIDF123(x, N_u, dK_u):
    """iF = bmIDF123(x, N_u, dK_u)

    Strict deterministic baseline port from MATLAB.
    """
    if N_u.shape[0] == 1:
        iF = bmIDF1(x, N_u, dK_u)
    elif N_u.shape[0] == 2:
        iF = bmIDF2(x, N_u, dK_u)
    elif N_u.shape[0] == 3:
        iF = bmIDF3(x, N_u, dK_u)
    else:
        raise ValueError("Unsupported size for N_u")
    return iF
