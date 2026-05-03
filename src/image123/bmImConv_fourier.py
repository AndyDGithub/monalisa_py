from __future__ import annotations

import numpy as np
from src.image123.bmImDFT import bmImDFT
from src.image123.bmImIDF import bmImIDF

def bmImConv_fourier(a, b):
    """Strict deterministic baseline port from MATLAB."""
    # Convert inputs to 1D arrays if they are currently vectors
    if np.ndim(a) == 1 and np.ndim(b) == 1:
        a = a.flatten()
        b = b.flatten()

    # Compute the Fourier transforms of the inputs
    Fa = bmImDFT(a)
    Fb = bmImDFT(b)

    # Multiply the Fourier transforms element-wise
    out = Fa * Fb

    # Compute the inverse Fourier transform to get the result
    out = bmImIDF(out)

    return out
