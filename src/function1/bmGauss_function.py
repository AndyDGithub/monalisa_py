import numpy as np
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape to resolve ModuleNotFoundError

def bmGauss_function(x, myMu, mySigma):
    f = (1 / (np.sqrt(2 * np.pi) * mySigma)) * np.exp(-((x - myMu) ** 2) / (mySigma ** 2) / 2)
    return f
