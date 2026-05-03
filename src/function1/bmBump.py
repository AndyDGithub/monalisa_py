import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmBump(x: np.ndarray, xCut: float) -> np.ndarray:
    """Compute the bump function."""
    xCut = abs(xCut)
    x = x / xCut
    n = np.abs(x)
    with np.errstate(divide='ignore', invalid='ignore'):
        y = np.exp(-1.0 / (1 - n**2)) * np.exp(1)
    y[n >= 1] = 0
    return y

from src.geom123 import bmTraj
