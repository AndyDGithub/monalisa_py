import numpy as np

def bmVarargin(*args):
    """
    Distribute positional arguments with None padding for missing entries.

    Mirrors MATLAB's bmVarargin(varargin) which returns the elements of the
the
    cell array varargin{} and fills missing outputs with [].

    Usage:
        C, N_u, n_u, dK_u = bmVarargin(C, N_u, n_u)      # dK_u = None
        C, N_u              = bmVarargin(C)                # N_u = None
        vals                = bmVarargin(a, b, c)          # returns [a, b,
b,
b, c]
    """
    return list(args)


def bmVarargin_unpack(args_list, n):
    """Unpack args_list to exactly n values, padding with None."""
    result = list(args_list) if args_list else []
    while len(result) < n:
        result.append(None)
    return result[:n]


import numpy as np

def bmRotation3(psi, theta, phi):
    """Compute the 3x3 rotation matrix using Euler angles (psi, theta, phi)
phi).

    This function calculates the rotation matrix R by means of matrix
    multiplication of three single matrices that each represent the element
element
    elemental
    rotation around an axis (X, Y, Z or 1,2,3). The rotation matrix is calc
calculated as R = Z(phi)*Y(theta)*Z(psi).

    Parameters:
        psi (double): Euler angle of the third elementary rotation matrix.
        theta (double): Euler angle of the second elementary rotation matri
matrix.
        phi (double): Euler angle of the first elementary rotation matrix.

    Returns:
        R (np.ndarray): A 3x3 rotation matrix.
    """

    # Define rotation matrices based on Euler angles
    R_psi = np.array([
        [np.cos(psi), -np.sin(psi), 0],
        [np.sin(psi), np.cos(psi), 0],
        [0, 0, 1]
    ])

    R_theta = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

    R_phi = np.array([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi), np.cos(phi), 0],
        [0, 0, 1]
    ])

    # Calculate rotation matrix
    R = np.dot(R_phi, np.dot(R_theta, R_psi))

    return R


from src.geom123 import bmTraj
