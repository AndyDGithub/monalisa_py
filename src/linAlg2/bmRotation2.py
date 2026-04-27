import numpy as np
from src.arrayUtility import bmBlockReshape

def bmRotation2(phi):
    R = np.array([[np.cos(phi), -np.sin(phi)],
                  [np.sin(phi), np.cos(phi)]])
    return R
