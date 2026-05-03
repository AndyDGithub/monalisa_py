import numpy as np

# %%
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
#
# Function: bmVolumeElement_replace_cartesian
# Purpose: Replace volume element using Cartesian coordinates.
#
# The MATLAB reference implementation removes the outermost
# boundaries of an N-dimensional array and then re-appends them
# so that the resulting vector has the same layout as MATLAB's
# v(:)' operation.
#
# Note: This Python implementation follows the MATLAB logic
# closely, using numpy slicing and concatenation. The final
# output is a flattened 1-D array that matches the MATLAB
# row-vector return value.

def bmVolumeElement_replace_cartesian(arg_v, N_u):
    """
    Replace volume element using Cartesian coordinates.

    Parameters
    ----------
    arg_v : np.ndarray
        Input array to be modified.
    N_u : tuple or array-like
        Dimensions of the input array.

    Returns
    -------
    np.ndarray
        Flattened array with boundary elements removed and re-added
        as in the MATLAB implementation.
    """
    # Ensure array and reshape to original dimensions
    v = np.asarray(arg_v)
    imDim = len(N_u)
    v = v.reshape(N_u)

    if imDim == 1:
        # Remove first and last elements, then re-append them
        v = np.delete(v, [0, -1])
        v = np.concatenate((v[:1], v, v[-1:]))

    elif imDim == 2:
        # Remove outermost rows and columns
        v = np.delete(v, [0, -1], axis=1)  # columns
        v = np.delete(v, [0, -1], axis=0)  # rows
        # Re-append removed borders
        v = np.concatenate((v[:1, :], v, v[-1:, :]), axis=0)
        v = np.concatenate((v[:, :1], v, v[:, -1:]), axis=1)

    elif imDim == 3:
        # Remove outermost slices, columns, and rows in MATLAB order
        v = np.delete(v, 0, axis=2)   # first depth slice
        v = np.delete(v, -1, axis=2)  # last depth slice
        v = np.delete(v, 0, axis=1)   # first column
        v = np.delete(v, -1, axis=1)  # last column
        v = np.delete(v, 0, axis=0)   # first row
        v = np.delete(v, -1, axis=0)  # last row
        # Re-append removed borders
        v = np.concatenate((v[:1, :, :], v, v[-1:, :, :]), axis=0)
        v = np.concatenate((v[:, :1, :], v, v[:, -1:, :]), axis=1)
        v = np.concatenate((v[:, :, :1], v, v[:, :, -1:]), axis=2)

    # Flatten to a 1-D array as MATLAB returns a row vector
    return v.ravel()
