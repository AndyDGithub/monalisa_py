from src.image123.bmImReshape import bmImReshape

def bmImSqueeze(argIm):
    """
    Squeeze the input image and return additional parameters.

    Parameters
    ----------
    argIm : numpy.ndarray
        Input image array.

    Returns
    -------
    tuple
        Tuple containing the squeezed image, its dimensionality,
        its size, and, if requested, the original dimensions that were
        removed during squeezing.
    """
    # Use the helper to perform the squeeze and obtain the original
    # shape information that MATLAB's bmImReshape would return.
    outIm, imDim, imSize, s1, s2, s3 = bmImReshape(np.squeeze(argIm))

    # MATLAB's bmImSqueeze returns the first three fixed outputs
    # followed by a variable number of optional outputs depending on
    # the caller's requested number of outputs (nargout). In Python,
    # we emulate this by returning a tuple that always contains the
    # three fixed outputs and then includes the optional values only
    # if they are requested. Since Python functions cannot introspect
    # the number of expected outputs, we simply return all three
    # optional values and let callers ignore unused ones.
    return outIm, imDim, imSize, s1, s2, s3
