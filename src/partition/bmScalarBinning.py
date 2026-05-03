import numpy as np

def bmScalarBinning(x, nBin):
    """
    Generate a binning mask for scalar data.

    The function sorts the input values, assigns them to `nBin` contiguous
    bins, then restores the original order.  The resulting mask has shape
    (nBin, N) where each row corresponds to a bin and each column to an
    element of the original input array.

    Parameters
    ----------
    x : np.ndarray
        1-D array of scalar values.
    nBin : int
        Number of bins to create.

    Returns
    -------
    myMask : np.ndarray
        Boolean mask of shape (nBin, len(x)).
    """
    # Flatten input and cast to numpy array
    x = np.asarray(x).ravel()
    N = x.size
    if N == 0:
        # Return an empty mask when input is empty
        return np.zeros((nBin, 0), dtype=bool)

    # Length of each bin in the sorted order
    myBinLength = N // nBin

    # Indices that sort the array
    myPerm = np.argsort(x)

    # Create the mask in sorted order
    myMask = np.zeros((nBin, N), dtype=bool)
    for i in range(nBin):
        start_idx = i * myBinLength
        end_idx = (i + 1) * myBinLength
        myMask[i, start_idx:end_idx] = True

    # Remaining elements go to the last bin
    myMask[-1, nBin * myBinLength :] = True

    # Restore original order
    myInvPerm = np.argsort(myPerm)
    myMask = myMask[:, myInvPerm]

    return myMask
