import numpy as np
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape from arrayUtility

def bmRotation2_inv(phi):
    phi   = -phi
    R_inv = bmBlockReshape([np.cos(phi), -np.sin(phi),
                           np.sin(phi),  np.cos(phi)], shape=(2, 2))
    return R_inv
