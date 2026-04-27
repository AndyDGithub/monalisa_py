from src.imageN.bmImDim import bmImDim
import numpy as np

def bmImReshape(argIm):
    # [outIm, imDim, imSize, varargout] = bmImReshape(argIm)
    # 
    # This function returns the number of dimensions and size of the input
    # array. Can optionally return the x, y and z size, which are the size of
    # the first three dimensions of the input array. If the input array is a
    # vector (1D), the returned array is a column vector.
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
    # argIm (numpy.ndarray): The array of which the dimension and size should be
    # returned. Cannot be empty.
    # 
    # Returns:
    # outIm (numpy.ndarray): Same as argIm except if argIm is 1D, then the outIm is
    # reshaped to a column vector.
    # imDim (int): The number of dimensions.
    # imSize (list): The size of each dimension as a list.
    # varargout{1}: Integer containing the size of the first dimension.
    # varargout{2}: Integer containing the size of the second dimension. 
    # Empty if imDim < 2
    # varargout{3}: Integer containing the size of the third dimension. 
    # Empty if imDim < 3

    outIm = argIm
    imDim = bmImDim(argIm)
    
    # Throw an error if argIm is empty
    if imDim == 0:
        raise ValueError("The image dimension is 0.")
    
    # Turn input into column vector if input is a vector
    if imDim == 1:
        outIm = outIm.ravel()

    # Get sizes of the first three dimensions
    [imDim, imSize, s1, s2, s3] = bmImDim(outIm)

    # Return if required
    varargout = []
    if len([x for x in (1, 2, 3) if x <= len(varargout)]) > 0:
        varargout.append(imSize[0])
    if len([x for x in (1, 2, 3) if x <= 1 + len(varargout)]) > 0:
        varargout.append(imSize[1])
    if len([x for x in (1, 2, 3) if x <= 2 + len(varargout)]) > 0:
        varargout.append(imSize[2])

    return outIm, imDim, imSize, varargout
