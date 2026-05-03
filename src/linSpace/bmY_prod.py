import numpy as np

def bmVarargin(*args):
    """
    Distribute positional arguments with None padding for missing entries.

    Mirrors MATLAB's bmVarargin(varargin) which returns the elements of the
the
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

from src.geom123 import bmTraj

def bmRotation3(psi, theta, phi):
    """Compute the 3x3 rotation matrix using Euler angles (psi, theta, phi)
phi)
phi).

    This function calculates the rotation matrix R by means of matrix
    multiplication of three single matrices that each represent the element
element
element
    rotation around an axis (X, Y, Z or 1,2,3). The rotation matrix 
is
    calculated as R = Z(phi)*Y(theta)*Z(psi).

    Parameters:
        psi (float): Euler angle of the third elementary rotation matrix.
        theta (float): Euler angle of the second elementary rotation matrix
matrix
matrix.
        phi (float): Euler angle of the first elementary rotation matrix.

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

from src.linSpace.bmY_ve_reshape import bmY_ve_reshape

def bmY_prod(y1, y2, d_n):
    """
    Compute the inner product of two 2-D complex arrays with optional weigh
weigh
weighting.

    This function implements the MATLAB routine bmY_prod which calculates:
        p = sum(conj(y1).*(y2.*d_n), 1)  if size(y1,1) > size(y1,2)
        p = sum(conj(y1).*(y2.*d_n), 2)  otherwise

    Parameters:
        y1 (np.ndarray): First complex array.
        y2 (np.ndarray): Second complex array of the same shape as y1.
        d_n (np.ndarray): Optional weighting array; reshaped to match y1.

    Returns:
        p (np.ndarray): Resulting array after weighted inner product.
    """
    if len(np.shape(y1)) > 2:
        raise ValueError("This function is for 2Dim arrays only.")
    if not (np.array_equal(np.shape(y1), np.shape(y2))):
        raise ValueError("Both arrays must have the same size.")

    d_n = bmY_ve_reshape(d_n, np.shape(y1))
    if y1.shape[0] > y1.shape[1]:
        p = np.sum(np.conj(y1) * (y2 * d_n), axis=1)
    else:
        p = np.sum(np.conj(y1) * (y2 * d_n), axis=2)

    return p
