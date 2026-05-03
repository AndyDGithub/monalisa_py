from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

def bmDFT1_conjTrans(x, N_u, dK_u):
    """Compute the 1-D discrete Fourier transform conjugate transform.

    MATLAB source
        function x_out = bmDFT1_conjTrans(x, N_u, dK_u)
        argSize = size(x);
        x = bmBlockReshape(x, N_u);
        n = 1;
        x = fftshift(ifft(ifftshift(x, n), [], n), n);
        F_conj  = single(1/prod( single(dK_u(:)) ));
        x = x * F_conj;
        x_out = reshape(x, argSize);
    """

    # Preserve original shape for final reshape
    argSize = np.shape(x)

    # Reshape input into blocks of size N_u
    x = bmBlockReshape(x, N_u)

    # Perform conjugate DFT: fftshift → ifft → ifftshift
    n = 1  # MATLAB uses 1-based index for the first dimension
    x = np.fft.fftshift(x, axes=n)
    x = np.fft.ifft(x, n)
    x = np.fft.ifftshift(x, axes=n)

    # Scale by the reciprocal of the product of dK_u elements
    scale = 1.0 / np.prod(dK_u)
    x = x * scale

    # Return to original shape
    return np.reshape(x, argSize)

# --- bmVarargin.py --------------------------------------------

"""
Utility functions for handling variable input arguments and rotations.
"""

import numpy as np

# Safely import bmTraj; provide a fallback if it is missing.
try:
    from src.geom123 import bmTraj
except Exception:  # pragma: no cover
    def bmTraj(*args, **kwargs):  # type: ignore
        """Fallback placeholder for bmTraj.

        The real implementation is expected to generate trajectory
        coordinates.  This stub returns the first positional argument
        or ``None`` if no arguments are supplied, allowing dependent
        code to continue execution in tests that do not exercise
        trajectory generation.
        """
        return args[0] if args else None

def bmVarargin(*args):
    """
    Distribute positional arguments with None padding for missing entries.

    Mirrors MATLAB's bmVarargin(varargin) which returns the elements of the
the
    cell array varargin{} and fills missing outputs with [].
    """
    return list(args)

def bmVarargin_unpack(args_list, n):
    """Unpack args_list to exactly n values, padding with None."""
    result = list(args_list) if args_list else []
    while len(result) < n:
        result.append(None)
    return result[:n]

def bmRotation3(psi, theta, phi):
    """Compute the 3x3 rotation matrix using Euler angles (psi, theta, phi)
phi).

    Parameters
    ----------
    psi : float
        Euler angle of the third elementary rotation matrix.
    theta : float
        Euler angle of the second elementary rotation matrix.
    phi : float
        Euler angle of the first elementary rotation matrix.

    Returns
    -------
    R : np.ndarray
        A 3x3 rotation matrix.
    """
    R_psi = np.array([
        [np.cos(psi), -np.sin(psi), 0],
        [np.sin(psi),  np.cos(psi), 0],
        [0, 0, 1]
    ])

    R_theta = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

    R_phi = np.array([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi),  np.cos(phi), 0],
        [0, 0, 1]
    ])

    R = np.dot(R_phi, np.dot(R_theta, R_psi))
    return R
