import numpy as np

def bmTraj_randomPartialCartesian1(N_u, dK_u, perOne):
    t = np.arange(-N_u/2, N_u/2) * dK_u
    m = (np.random.rand(1, N_u) < perOne).ravel()
    t = t[m]
    return t
