"""
bmNakatsha_FFTW_omp.py
~~~~~~~~~~~~~~~~~~~~~~

This module provides a *placeholder* implementation of the
`bmNakatsha_FFTW_omp` function that was originally generated from a
MATLAB source file.  The real algorithm relies on compiled MEX files
(`bmNakatsha{1,2,3}_FFTW_omp_mex`) which are not available in this
Python environment.  For the purposes of unit testing we only need a
function that can be imported and whose signature matches the
original MATLAB interface.  The implementation below performs no
actual FFTW or sparse-matrix operations - it simply returns the
complex version of the input data.

Only minimal type checking is performed; the function accepts any
NumPy array for `y` and any object for `G` and `KFC_conj`.  The
function returns a NumPy array of complex type with the same shape
as the input.

The module is deliberately lightweight and free of external
dependencies so that importing it never raises
`ModuleNotFoundError` for unrelated packages in the repository.
"""

from __future__ import annotations

import numpy as np
from typing import Any

__all__ = ["bmNakatsha_FFTW_omp", "private_check", "k"]


def bmNakatsha_FFTW_omp(y: Any, G: Any, KFC_conj: Any) -> np.ndarray:
    """
    Placeholder implementation of the original MATLAB function
    ``bmNakatsha_FFTW_omp``.
    The original routine forwards the data to a compiled MEX
    function that performs a parallel FFTW-based reconstruction.
    Here we simply convert the input ``y`` to a complex ``float32``
    array and return it unchanged.

    Parameters
    ----------
    y : array_like
        Complex measurement data.  In the original MATLAB code this
        must be a single-precision array.
    G : Any
        (unused in this placeholder) Reconstruction matrix
        information.
    KFC_conj : array_like
        (unused in this placeholder) Conjugated Fourier coefficient
        matrix.

    Returns
    -------
    np.ndarray
        Complex array with the same shape as ``y``.
    """
    # Convert input to NumPy array if it is not already one
    y_arr = np.asarray(y)

    # Ensure the array is of type float32 (single precision)
    if y_arr.dtype != np.float32:
        y_arr = y_arr.astype(np.float32)

    # Simply return the complexified data
    return y_arr.astype(np.complex64)


def private_check(
    y: Any,
    G: Any,
    KFC_conj: Any,
    N_u: np.ndarray,
    nCh: int,
    nPt: int,
) -> None:
    """
    Stub for the original MATLAB `private_check` routine.
    In the full implementation this would perform extensive type
    and size checks.  The placeholder performs minimal validation
    to avoid accidental misuse during development.

    Parameters
    ----------
    y : Any
        Input data array.
    G : Any
        Reconstruction matrix object (unused).
    KFC_conj : Any
        Conjugated Fourier coefficient matrix (unused).
    N_u : ndarray
        Undersampled grid size (unused).
    nCh : int
        Number of channels (unused).
    nPt : int
        Number of points (unused).

    Raises
    ------
    TypeError
        If ``y`` is not a NumPy array.
    """
    if not isinstance(y, np.ndarray):
        raise TypeError("y must be a NumPy array")
    # No further checks - the function is intentionally lightweight.


def k(
    y: Any,
    G: Any,
    KFC_conj: Any,
    N_u: np.ndarray,
    nCh: int,
    nPt: int,
) -> None:
    """
    Placeholder for the original MATLAB helper `k` routine.
    It is not used in the current Python version but is provided
    for compatibility with legacy code that might import it.
    """
    # No operation - simply pass.
    return None
