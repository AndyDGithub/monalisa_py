from src.imDisp.bmImage2 import bmImage2
from src.imDisp.bmImage3 import bmImage3
from src.imDisp.bmImage4 import bmImage4
from src.imDisp.bmImage5 import bmImage5
import numpy as np

from src.arrayUtility.bmCell2Array import bmCell2Array
from src.varargin.bmVarargin import bmVarargin
from third_part.matlab_compat.matlab_native import double


def bmImage(argImage, varargin):
    # varargout = bmImage(argImage, varargin)
    #
    # This function creates an interactive figure displaying data from a 2D,
    # 3D, 4D or 5D array. If the data is complex, the absolute value will be
    # used.
    #
    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    #
    # Contributors:
    # Dominik Helbing (Documentation & Comments)
    # MattechLab 2024
    #
    # Parameters:
    # argImage (array): Contains the data to be displayed as an image.
    # varargin{1}: Object of class bmImageViewerParam, giving the parameters
    # for the image.
    #
    # Returns:
    # varargout{1}: Object of class bmImageViewerParam that was used in the
    # creation of the figure and containing the coordinates of placed
    # points.

    argParam = bmVarargin(varargin)
    uiwait_flag = False

    # Transform cell array to array
    if isinstance(argImage, list):
        argImage = np.array(bmCell2Array(argImage))

    # Turn complex values real
    if not np.isreal(argImage).all():
        argImage = np.abs(argImage)

    # Turn logical values to double for plotting
    if np.issubdtype(argImage.dtype, np.bool_):
        argImage = double(argImage)

    # Create image for 2, 3, 4 or 5 dimensions
    if argImage.ndim == 2:
        outParam = bmImage2(argImage, argParam, uiwait_flag)
    elif argImage.ndim == 3:
        outParam = bmImage3(argImage, argParam, uiwait_flag)
    elif argImage.ndim == 4:
        outParam = bmImage4(argImage, argParam, uiwait_flag)
    elif argImage.ndim == 5:
        outParam = bmImage5(argImage, argParam, uiwait_flag)

    # Return image parameters if required
    if len(varargin[0]) > 0:
        varargout = [outParam]

    return varargout
