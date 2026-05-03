from __future__ import annotations
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmPointReshape import bmPointReshape

import numpy as np


def bmFourierModulation(y, t, x_shift):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    t = bmPointReshape(t)
    nPt = t.shape[1]
    y = bmColReshape(y, nPt)
    nCh = y.shape[0]

    myExp = np.exp(-1j * 2 * np.pi * x_shift[:, np.newaxis] * t)
    y_out = np.reshape(y * myExp, (nCh, nPt))
    
    return y_out
