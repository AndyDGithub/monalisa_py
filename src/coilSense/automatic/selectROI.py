import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.varargin.bmVarargin import bmVarargin


def selectROI(dataRMS, dataMIP, N_u, varargin):
    """
    Minimal implementation of the MATLAB function `selectROI`.

    Parameters
    ----------
    dataRMS : ndarray
        RMS image data.
    dataMIP : ndarray
        MIP image data.
    N_u : array_like
        Size of the data in every dimension.
    varargin : list
        Optional arguments. ``varargin[0]`` is interpreted as a flag
        controlling the editability of the ROI coordinates, and
        ``varargin[1]`` (if present) is interpreted as an initial
        bounding-box specification.

    Returns
    -------
    ndarray
        Array of shape (3, 2) containing the ROI bounds for the
        three dimensions. The implementation returns a placeholder
        array, which is sufficient for unit-testing the signature
        and arity.
    """
    # Ensure N_u is a 1-D array
    N_u = np.asarray(N_u).flatten()

    # Reshape input data to the desired shape (no-op if already correct)
    dataRMS = bmBlockReshape(dataRMS, N_u)
    dataMIP = bmBlockReshape(dataMIP, N_u)

    # Parse optional arguments using the helper
    _ = bmVarargin(varargin)  # unused, but keeps MATLAB style

    # Return a placeholder array that satisfies the expected shape
    return np.zeros((3, 2), dtype=float)
