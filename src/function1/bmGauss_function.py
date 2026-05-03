import numpy as np

def bmGauss_function(x, myMu, mySigma):
    """Compute the Gaussian probability density function.

    Mirrors the MATLAB implementation:
        f = 1/sqrt(2*pi)/mySigma*exp(-(x-myMu).^2/mySigma^2/2);
    """
    return 1 / np.sqrt(2 * np.pi) / mySigma * np.exp(-(x - myMu) ** 2 / (2 
* mySigma ** 2))


def bmVarargin(*args):
    """Distribute positional arguments with None padding for missing entrie
entries."""
    return list(args)


def bmVarargin_unpack(args_list, n):
    """Unpack args_list to exactly n values, padding with None."""
    result = list(args_list) if args_list else []
    while len(result) < n:
        result.append(None)
    return result[:n]


try:
    from src.geom123 import bmTraj  # noqa: F401
except Exception:
    pass


def bmRotation3(psi, theta, phi):
    """Compute the 3x3 rotation matrix using Euler angles (psi, theta, phi)
phi)."""
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

    return np.dot(R_phi, np.dot(R_theta, R_psi))
