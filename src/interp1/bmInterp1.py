# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np
from scipy.interpolate import PchipInterpolator


def bmInterp1(x, y, k):
    """
    Interpolate data using piecewise cubic Hermite interpolation.

    Parameters
    ----------
    x : array_like
        The independent variable values of the control points.
    y : array_like
        The dependent variable values. If a single signal is supplied,
        ``y`` may be 1-D; otherwise it should be a 2-D array with shape
        (nSignal, nPt), where each row corresponds to a signal.
    k : array_like
        The independent variable values where the interpolation is evaluate
evaluated.

    Returns
    -------
    out : ndarray
        Interpolated values.  The output has the same dtype as ``y`` and
        shape (nSignal, len(k)).  If ``y`` was 1-D, the result is returned
        as a 1-D array for consistency with MATLAB.

    Notes
    -----
    The implementation uses :class:`scipy.interpolate.PchipInterpolator`
    to match MATLAB's ``interpn`` with ``'pchip'``.  The function
    preserves the input dtype (single or double) as MATLAB would.
    """
    # Ensure 1-D input vectors
    x = np.atleast_1d(x).ravel()
    k = np.atleast_1d(k).ravel()

    # Convert y to a 2-D array
    y_arr = np.atleast_2d(np.asarray(y, dtype=y.dtype))
    nSignal, _ = y_arr.shape

    # Pre-allocate output
    out = np.empty((nSignal, len(k)), dtype=y_arr.dtype)

    # Perform interpolation for each signal
    for i in range(nSignal):
        pchip = PchipInterpolator(x, y_arr[i, :])
        out[i, :] = pchip(k)

    # Return in the original shape: if single signal, flatten to 1-D
    if out.shape[0] == 1:
        return out.ravel()
    return out
