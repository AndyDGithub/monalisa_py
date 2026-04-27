# bmAffineFit.py
import numpy as np
from numpy import squeeze, isnan, isinf


def bmAffineFit(argImagesTable, argX, errorTh=None, lowerBound=None, upperBound=None):
    """
    Affine fit of images.

    Parameters
    ----------
    argImagesTable : ndarray
        The image table to fit.
    argX : ndarray
        List of X coordinates corresponding to each image in argImagesTable.
    errorTh : float or int, optional
        Error threshold for bad fits. Default is None.
    lowerBound : float or int, optional
        Lower bound for acceptable B_map values. Default is None.
    upperBound : float or int, optional
        Upper bound for acceptable B_map values. Default is None.

    Returns
    -------
    a_map : ndarray
        Affine map slope for each image.
    b_map : ndarray
        Affine map intercept for each image.
    errorMask : ndarray
        Mask indicating which fits are considered bad (NaN where True).
    fitImages : ndarray
        Fitted images.
    """
    mySize = argImagesTable.shape[:-1]
    mySize = [np.prod(mySize), mySize[-1]]

    if len(argX) != mySize[1]:
        a_map = np.zeros(mySize, dtype=float)
        b_map = np.zeros(mySize, dtype=float)
        print('Wrong list of arguments')
        return a_map, b_map, np.zeros_like(argImagesTable, dtype=bool), np.zeros_like(argImagesTable)

    imagesTable = argImagesTable.reshape(mySize)
    iMax = mySize[1]
    x = squeeze(argX).T

    a_map = np.zeros(mySize, dtype=float)
    b_map = np.zeros(mySize, dtype=float)

    xTable = np.tile(x, [mySize[0], 1])
    zTable = imagesTable

    MeanX = np.mean(xTable, axis=1)
    MeanZ = np.mean(zTable, axis=1)
    MeanX2 = np.mean(xTable**2, axis=1)
    MeanXZ = np.mean(xTable * zTable, axis=1)

    a_map = (MeanX2 * MeanZ - MeanX * MeanXZ) / (MeanX2 - MeanX**2)
    b_map = (MeanXZ - MeanX * MeanZ) / (MeanX2 - MeanX**2)

    a_map_table = np.tile(a_map, [iMax, 1])
    b_map_table = np.tile(b_map, [iMax, 1])

    myFit = a_map_table + b_map_table * xTable
    myError = np.sqrt(np.mean((myFit - zTable)**2 / myFit**2, axis=1))

    if errorTh is not None:
        errorMask = (myError > errorTh)
    else:
        errorMask = np.zeros_like(a_map, dtype=bool)

    errorMask += isnan(a_map) + isnan(b_map) + isinf(a_map) + isinf(b_map)

    if lowerBound is not None:
        errorMask += (b_map < lowerBound)
    if upperBound is not None:
        errorMask += (b_map > upperBound)

    a_map[errorMask] = np.nan
    b_map[errorMask] = np.nan

    fitImages = myFit.reshape(argImagesTable.shape)

    return a_map, b_map, errorMask, fitImages
