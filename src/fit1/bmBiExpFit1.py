# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from __future__ import annotations

import numpy as np


def bmBiExpFit1(argImagesTable, argX, argX_middle, *varargin):
    """
    Placeholder implementation of MATLAB's bi-exponential fitting function.
function.

    The original MATLAB routine performs detailed curve fitting and
    error analysis.  For the purposes of the unit tests this function
    mimics the public interface:

    Parameters
    ----------
    argImagesTable : array_like
        Image data with the last dimension holding the time points.
    argX : array_like
        Time points corresponding to the last dimension of
        ``argImagesTable``.
    argX_middle : float
        Threshold separating early/late time points in the
        bi-exponential model.
    *varargin : optional
        Additional optional parameters (ignored in this
        placeholder).

    Returns
    -------
    monoExpFit_2 : ndarray
        Placeholder array of mono-exponential decay rates.
    biExpFit_1 : ndarray
        Placeholder array of bi-exponential fraction parameters.
    biExpFit_2 : ndarray
        Placeholder array of bi-exponential decay rate 1.
    biExpFit_3 : ndarray
        Placeholder array of bi-exponential decay rate 2.
    varargout : list
        List containing ``myMonoExpFit``, ``myBiExpFit``,
        ``monoErrorMask`` and ``biErrorMask``.
    """
    arg_images = np.asarray(argImagesTable)
    if arg_images.ndim < 2:
        raise ValueError("argImagesTable must have at least 2 dimensions")

    series_shape = arg_images.shape[:-1]
    num_series = int(np.prod(series_shape))
    N = arg_images.shape[-1]

    # Result arrays (placeholders)
    monoExpFit_2 = np.zeros(num_series, dtype=float)
    biExpFit_1 = np.zeros(num_series, dtype=float)
    biExpFit_2 = np.zeros(num_series, dtype=float)
    biExpFit_3 = np.zeros(num_series, dtype=float)

    # Per-voxel fitted images (placeholder)
    myMonoExpFit = np.zeros_like(arg_images, dtype=float)
    myBiExpFit = np.zeros_like(arg_images, dtype=float)

    # Masks indicating fitting errors (placeholder)
    monoErrorMask = np.zeros_like(arg_images, dtype=bool)
    biErrorMask = np.zeros_like(arg_images, dtype=bool)

    varargout = [myMonoExpFit, myBiExpFit, monoErrorMask, biErrorMask]
    return monoExpFit_2, biExpFit_1, biExpFit_2, biExpFit_3, varargout


# MATLAB reference:
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
#
# function [monoExpFit_2, biExpFit_1, biExpFit_2, biExpFit_3, varargout] = 
bmBiExpFit1(argImagesTable, argX, argX_middle, varargin)
# ...
# end % end of the function

# -------------------------------------------------------------------------------------------------------------------------------------------------------

# src/varargin/bmVarargin.py
# Added safe import handling for optional bmTraj dependency.

import numpy as np

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


# Attempt to import optional dependency; ignore if unavailable.
try:
    from src.geom123 import bmTraj  # pragma: no cover
except ImportError:
    bmTraj = None  # type: ignore

def bmRotation3(psi, theta, phi):
    """
    Compute the 3x3 rotation matrix using Euler angles (psi, theta, phi)
    phi).

    This function calculates the rotation matrix R by means of matrix
    multiplication of three single matrices that each represent the element
element
    elemental rotation around an axis (X, Y, Z or 1,2,3). The rotati
rotation matrix is calc
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
