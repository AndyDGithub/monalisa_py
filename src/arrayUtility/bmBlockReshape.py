import numpy as np

def bmBlockReshape(argIn, N_u):
    """
    Reshape the input array or list to blocks of size N_u.

    Parameters
    ----------
    argIn : array_like or list
        Data to reshape. Can be a numpy array or a list/tuple of arrays.
    N_u : array_like
        Size of each block (same for all channels). Must be integers.

    Returns
    -------
    ndarray or list
        Reshaped data. If `argIn` is a single channel, the trailing dimensi
dimensi
dimension is removed
        to emulate MATLAB's behaviour.

    Notes
    -----
    This function mirrors MATLAB's `bmBlockReshape` which recursively proce
proce
processes cell
    arrays, handles empty inputs, and reshapes to `[N_u, nCh]` where `nCh`
    is the number of blocks. The implementation below is type-safe, works
    with numpy arrays and lists, and preserves the original MATLAB logic.
    """
    # Handle list input recursively
    if isinstance(argIn, list):
        return [bmBlockReshape(item, N_u) for item in argIn]

    # Convert to numpy array
    argIn = np.asarray(argIn)

    # Empty input
    if argIn.size == 0:
        return np.array([])

    # Ensure N_u is integer array
    N_u = np.asarray(N_u, dtype=int).ravel()
    if N_u.size == 0:
        raise ValueError("N_u must contain at least one integer")

    # Compute number of channels
    prod_N_u = int(np.prod(N_u))
    nCh = int(argIn.size / prod_N_u)
    if nCh * prod_N_u != argIn.size:
        raise ValueError("argIn size is not compatible with N_u")

    # Reshape to [N_u, nCh]
    out = argIn.reshape(tuple(N_u) + (nCh,))
    # Remove trailing dimension if only one channel
    if nCh == 1:
        out = out.squeeze(-1)
    return out

import numpy as np

def bmRotation3(psi, theta, phi):
    """Compute the 3x3 rotation matrix using Euler angles (psi, theta, phi)
phi) and (phi).
    
    This function calculates the rotation matrix R by means of matrix
    multiplication of three single matrices that each represent the element
element
    elemental
    elemental
    rotation around an axis (X, Y, Z or 1,2,3). The rotation matrix is calc
calc
    calculated as R = Z(phi)*Y(theta)*Z(psi).
    
    Parameters:
        psi (double): Euler angle of the third elementary rotation matrix.
        theta (double): Euler angle of the second elementary rotation matri
matri
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
    b,
    b, c]
    """
    return list(args)

import numpy as np

def bmVarargin_unpack(args_list, n):
    """Unpack args_list to exactly n values, padding with None."""
    result = list(args_list) if args_list else []
    while len(result) < n:
        result.append(None)
    return result[:n]
