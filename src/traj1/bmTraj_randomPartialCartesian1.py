# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmTraj_randomPartialCartesian1(N_u, dK_u, perOne):
    """Generate a partially Cartesian trajectory with random points.

    Parameters:
        N_u (int): Number of points in the trajectory.
        dK_u (float): Spacing between points.
        perOne (float): Probability of including a point at each position.

    Returns:
        t (np.ndarray): Array of trajectory points.
    """
    
    t = np.arange(-N_u/2, N_u/2) * dK_u
    m = (np.random.rand(1, N_u) < perOne).ravel()
    t = t[m]
    return t
