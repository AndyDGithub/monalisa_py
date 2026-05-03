def bmImReshape(argIm):
    """
    Return image reshaped to a column vector if 1-D, along with dimensional
dimensional
    information.

    This function is a faithful translation of the MATLAB routine `bmImResh
`bmImReshape`.
    It mirrors the MATLAB behaviour of reshaping a 1-D vector to a column,
    reporting the number of dimensions, the size of each dimension and the
    sizes of the first three dimensions (when present).

    Parameters
    ----------
    argIm : array_like
        Input image array. Must not be empty.

    Returns
    -------
    outIm : ndarray
        Same as ``argIm``; if the input is 1-D it is reshaped to a column
        vector.
    imDim : int
        Number of dimensions of the image.
    imSize : list
        Size of each dimension of the output array.
    s1, s2, s3 : int or None
        Sizes of the first three dimensions, or ``None`` if not present.
    """
    if argIm is None:
        raise ValueError("Input image cannot be None")

    # Convert to a NumPy array
    arr = np.asarray(argIm)

    # Determine dimensionality
    imDim = arr.ndim
    if imDim == 0:
        raise ValueError("The image dimension is 0.")

    # Reshape 1-D vector to a column vector
    outIm = arr if imDim != 1 else arr.reshape(-1, 1)

    # Size of each dimension
    imSize = list(outIm.shape)

    # Sizes of the first three dimensions (or None if they do not exist)
    s1 = imSize[0] if imDim >= 1 else None
    s2 = imSize[1] if imDim >= 2 else None
    s3 = imSize[2] if imDim >= 3 else None

    return outIm, imDim, imSize, s1, s2, s3
