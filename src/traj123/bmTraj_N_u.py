from src.arrayUtility.bmPointReshape import bmPointReshape
import numpy as np

def bmTraj_N_u(t):
    t = bmPointReshape(t)
    imDim = np.shape(t)[1]
    N_u = 256  # Magic number

    N_u = np.repeat(N_u, imDim)
    N_u = N_u.T

    return N_u
