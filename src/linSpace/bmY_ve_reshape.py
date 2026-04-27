import numpy as np

def bmY_ve_reshape(ve, y_size):
    # Transform to row vector
    y_size = y_size[::-1]

    # Return out of the function if ve already has the correct size
    if (np.shape(ve)[0] == y_size[0]) and (np.shape(ve)[1] == y_size[1]):
        ve_out = ve
        return ve_out

    # Get number of points and channels
    nPt      = y_size[0]
    nCh      = y_size[1]

    # Throw error if y has only one element
    if (nPt == 1) and (nCh == 1):
        raise ValueError("ve is not reshapable in the given size.")

    # Get size of ve
    s1 = np.shape(ve)[0]
    s2 = np.shape(ve)[1]

    # Check if y has the data of each channels as rows (rawFlag = true) or
    # columns (rawFlag = false)
    rawFlag = False
    if nPt < nCh:
        # Changes values for variables if each row represents a channel
        rawFlag = True
        temp = nPt
        nPt  = nCh
        nCh  = temp

    if s1 == 1 and s2 == 1:
        # If ve is a single value, repeat it for every point
        ve_out = ve * np.ones((nPt, nCh))

    elif s1 > 1 and s2 == 1:
        # If ve is a column vector, repeat it for every channel
        ve_out = np.repeat(ve, nCh, axis=0)

    elif s1 == 1 and s2 > 1:
        # If ve is a row vector, change it to a column vector and repeat it for
        # every channel
        ve_out = np.repeat(ve.reshape(-1, 1), nCh, axis=0)

    elif s1 > 1 and s2 > 1:
        # If ve is already an array, transpose if the sizes are not correct
        if not (s1 == nPt) or not (s2 == nCh):
            ve_out = ve.T

    # Transpose if each row represents a channel
    if rawFlag:
        ve_out = ve_out.T

    # Throw error if reshaping failed
    if not np.array_equal(np.shape(ve_out), y_size):
        raise ValueError("ve is not reshapable in the given size.")

    return ve_out
