from src.image123.bmImReshape import bmImReshape
import numpy as np
from third_part.matlab_compat.matlab_native import single
from src.varargin.bmVarargin import bmVarargin

def bmImPseudoDiffusion(argIm, varargin):
    # myIm = bmImPseudoDiffusion(argIm, varargin)
    # 
    # This function performes smoothing on data by averaging the data over its
    # direct neighbors (not diagonal), by diffusing the data. The edge cases
    # take as neighbors the edges on the other side as a circular shift is
    # used. This function can be applied to 1D, 2D and 3D data.
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
    # argIm (array): The data that should be diffused.
    # varargin{1}: Integer containing the number of iterations of averaging
    # applied to smooth the data. The default value is 1.
    # 
    # Returns:
    # myIm (data): The data smoothed.

    # Initialize arguments
    nIter = bmVarargin(varargin)
    # Set default value for number of iterations if empty
    nIter = 1 if not nIter else nIter
    # Get dimension and size of input data (also get data as column vector if
    # argIm is 1D)
    myIm, imDim, imSize = bmImReshape(single(np.squeeze(argIm)))

    # Create shift list used to access all neighbors and the original datapoint
    # with a circular shift.
    if imDim == 1:
        myShiftList = np.array([0, 1, -1])
    elif imDim == 2:
        myShiftList = np.array([[0, 0], [0, 1], [0, -1], [1, 0], [-1, 0]])
    else:  # imDim == 3
        myShiftList = np.array(
            [[0, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, -1, 0],
              [1, 0, 0], [-1, 0, 0]]
        )
    # Get number of shifts = number of direct neighbors (not diagonal)
    nShift = myShiftList.shape[0]

    # Do smoothing
    temp_im = np.zeros(imSize, "single")
    for j in range(nShift):
        temp_im += np.roll(myIm, myShiftList[j], axis=tuple(range(imDim)))

    myIm = temp_im / (imDim * 2 + 1)
    myIm = np.reshape(myIm, argIm.shape)

    return myIm
