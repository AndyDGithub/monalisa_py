from pathlib import Path
import os
import numpy as np
try:
    from pydicom import dcmread
except ImportError:
    dcmread = None
from src.readWrite.bmCheckDir import bmCheckDir
from src.readWrite.bmGetDir import bmGetDir
from src.readWrite.bmNameList import bmNameList
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Import the missing function


def bmDicomRead(*args):
    """
    Read a sequence of 2-D DICOM images from a directory or a single file.

    Parameters
    ----------
    *args : tuple
        Optional keyword/value pairs. Valid keys are 'Dir', 'Path' or 'File'. Each key must be
        followed by the corresponding value.

    Returns
    -------
    imagesTable : numpy.ndarray
        3-D array containing all images (x, y, nImages). Returned as ``float64`` (Python ``double``).
    myDir : str
        Directory from which the images were read.
    """
    # default values
    myFile = None
    myDir = None
    myPath = None

    dirFlag = pathFlag = fileFlag = False

    # -------------------------------------------------------------
    # Parse optional arguments
    # -------------------------------------------------------------
    if not args:
        # no input → ask for directory
        myDir, myPath, _ = bmGetDir()
        dirFlag = True
        if isinstance(myDir, (int, float)):
            return np.array([]), myDir
    else:
        if len(args) > 2:
            raise ValueError('Wrong list of arguments')
        for i in range(0, len(args), 2):
            key = args[i]
            if key == 'Dir':
                myDir = args[i + 1]
                dirFlag = True
            elif key == 'Path':
                myPath = args[i + 1]
                pathFlag = True
            elif key == 'File':
                myFile = args[i + 1]
                fileFlag = True
            else:
                raise ValueError('Wrong list of arguments')

    # -------------------------------------------------------------
    # Resolve directory and path
    # -------------------------------------------------------------
    if dirFlag:
        myPath = os.path.join(myDir, '')
    elif pathFlag:
        myDir = os.path.dirname(myPath)
    elif fileFlag:
        myDir = os.path.dirname(myFile)
        myPath = os.path.join(myDir, '')
    else:
        raise ValueError('Directory or file not specified')

    if not bmCheckDir(myDir):
        return np.array([]), myDir

    # -------------------------------------------------------------
    # Read a single file
    # -------------------------------------------------------------
    if fileFlag:
        ds = dcmread(myFile)
        # In MATLAB the output is the pixel matrix itself.
        # We mimic that by returning the pixel array.
        return ds.pixel_array, myDir

    # -------------------------------------------------------------
    # Read a set of files from a directory
    # -------------------------------------------------------------
    file_list = bmNameList(myDir)
    file_list.sort()

    if not file_list:
        return np.array([]), myDir

    first_ds = dcmread(os.path.join(myPath, file_list[0]))
    first_img = first_ds.pixel_array

    if first_img.ndim != 2:
        raise ValueError('This function is for 2D images only')

    num_images = len(file_list)
    if num_images == 1:
        imagesTable = first_img
    else:
        # allocate array (x, y, nImages)
        imagesTable = np.zeros((*first_img.shape, num_images), dtype=first_img.dtype)
        for idx, fname in enumerate(file_list):
            img = dcmread(os.path.join(myPath, fname)).pixel_array
            imagesTable[:, :, idx] = img

    return bmBlockReshape(imagesTable, 2), myDir
