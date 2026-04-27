import numpy as np
from src.image123.bmImShiftList_to_image import bmImShiftList_to_image
from src.imDisp.bmImage import bmImage  # use the image helper
from src.image123.bmImResize import bmVarargin  # optional display flag


def bmImShiftList(argType, a, myPercent, varargin=None):
    """
    Generate a list of shift vectors according to the chosen shape.

    Parameters
    ----------
    argType : str
        One of 'sphere2', 'diamond2', 'square2', 'sphere3', 'diamond3',
        'square3'.  The last character denotes the dimensionality (2 or 3).
    a : int
        The radius of the grid (i.e. the maximum absolute coordinate value).
    myPercent : float
        The percentage of the maximal radius to include (0-100).
    varargin : list, optional
        Optional arguments; if the first element is truthy, the function
        will display a visual representation of the shift list.

    Returns
    -------
    myShiftList : ndarray
        A 2-D array of shape (N, dim) containing the shift vectors that
        satisfy the shape constraint.
    """
    if varargin is None:
        varargin = []

    # --- Determine image dimensionality ----------------------------------
    # The original MATLAB code used str2num(argType(end)), i.e. the last
    # character of the string.  We assume the last character is a digit
    # indicating the dimension (2 or 3).  Convert to int.
    try:
        imDim = int(argType[-1])
    except (IndexError, ValueError):
        raise ValueError(f"Cannot parse dimensionality from argType '{argType}'")

    # --- 1-D special case -----------------------------------------------
    if imDim == 1:
        out = np.arange(-a, a + 1)
        return out

    # --- Display flag ----------------------------------------------------
    # bmVarargin is expected to return a list of flags.  If the list is empty,
    # we default to False.
    disp_flag = bmVarargin(varargin) if isinstance(varargin, list) else False
    if not disp_flag:
        disp_flag = False

    # --- Compute radial limits -------------------------------------------
    r_min = a
    r_max = np.sqrt(imDim) * a
    r = r_min + (r_max - r_min) * myPercent / 100.0

    # --- Build grid -------------------------------------------------------
    # We generate a regular grid in the appropriate dimension and
    # flatten it to obtain the coordinate vectors.
    l = np.arange(-a, a + 1)
    if imDim == 2:
        X, Y = np.meshgrid(l, l, indexing='ij')
        x = X.ravel()
        y = Y.ravel()
        myGridd = np.column_stack((x, y))
    elif imDim == 3:
        X, Y, Z = np.meshgrid(l, l, l, indexing='ij')
        x = X.ravel()
        y = Y.ravel()
        z = Z.ravel()
        myGridd = np.column_stack((x, y, z))
    else:
        raise ValueError(f"Unsupported image dimensionality: {imDim}")

    # --- Shape constraints -----------------------------------------------
    # Map the shape name to the appropriate radius vector n.
    if argType == 'sphere2':
        n = np.sqrt(x**2 + y**2)
    elif argType == 'diamond2':
        n = np.abs(x) + np.abs(y)
    elif argType == 'square2':
        n = np.maximum(np.abs(x), np.abs(y))
    elif argType == 'sphere3':
        n = np.sqrt(x**2 + y**2 + z**2)
    elif argType == 'diamond3':
        n = np.abs(x) + np.abs(y) + np.abs(z)
    elif argType == 'square3':
        n = np.maximum(np.maximum(np.abs(x), np.abs(y)), np.abs(z))
    else:
        raise ValueError(f"Unknown shape type '{argType}'")

    # --- Select shift vectors --------------------------------------------
    n_mask = n <= r
    myShiftList = myGridd[n_mask, :]

    # --- Optional display -----------------------------------------------
    if disp_flag:
        # Visualise the shift list as an image using the helper.
        myImage = bmImShiftList_to_image(myShiftList)
        bmImage(myImage)

    return myShiftList
