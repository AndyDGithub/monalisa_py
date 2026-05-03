# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmGammaBar_H() -> float:
    """Compute the gyromagnetic ratio in 1/ms/mT."""
    return 267.5153151 / (2 * np.pi)  # in 1/ms/mT
