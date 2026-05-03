import numpy as np
from src.varargin.bmVarargin import bmVarargin

def bmImPseudoDiffusion_inMask(argIm, argMask, varargin):
    """myIm = bmImPseudoDiffusion_inMask(argIm, argMask, varargin)
    %
    % This function performes smoothing on data by averaging the data over 
its
    % direct neighbors (not diagonal), by diffusing the data. The edge case
cases
    % take as neighbors the edges on the other side as a circular shift is
    % used. This operation is restricted to only modify and consider the
    % unmasked data (where argMask is 1). The masked data keeps the values
    % of the original data. This function can be applied to 1D, 2D and 3D d
data.
    %
    % Authors:
    %   Bastien Milani
    %   CHUV and UNIL
    %   Lausanne - Switzerland
    %   May 2023
    %
    % Contributors:
    %   Dominik Helbing (Documentation & Comments)
    %   MattechLab 2024
    %
    % Parameters:
    %   argIm (array): The data that should be diffused.
    %   argMask (array): Of the same size as argIm and masks the regions wi
with 0
    %   that should not be modified and considered in the smoothing.
    %   varargin{1}: Integer containing the number of iterations of averagi
averaging
    %   applied to smooth the data. The default value is 1.
    %
    % Returns:
    %   myIm (data): The data smoothed at the unmasked points and the origi
original
    %    data at the masked points."""
    # Determine number of iterations from optional arguments
    nIter = bmVarargin(varargin)
    if not isinstance(nIter, int) or nIter <= 0:
        nIter = 1

    myIm = np.array(argIm, dtype=np.single)
    imSize = myIm.shape
    myMask = np.array(argMask, dtype=bool)

    # Handle 1-D input that may be a vector
    if imSize == ():
        imSize = (myIm.size,)

    myMask_neg = ~myMask

    # Construct shift list based on dimensionality
    if len(imSize) == 1:
        shiftList = [0, 1, -1]
    elif len(imSize) == 2:
        shiftList = [
            [0, 0], [0, 1], [0, -1],
            [1, 0], [-1, 0]
        ]
    elif len(imSize) == 3:
        shiftList = [
            [0, 0, 0], [0, 0, 1], [0, 0, -1],
            [0, 1, 0], [0, -1, 0],
            [1, 0, 0], [-1, 0, 0]
        ]
    else:
        raise ValueError("Unsupported dimensionality: must be 1, 2, or 3")

    # Main smoothing loop
    for _ in range(nIter):
        myIm[myMask_neg] = 0
        temp_im = np.zeros_like(myIm)
        myNumOfNeighb = np.zeros_like(myIm)

        for shift in shiftList:
            circ_shifted = np.roll(myIm, shift, axis=range(len(imSize)))
            temp_im += circ_shifted
            myNumOfNeighb += np.ones_like(circ_shifted, dtype=np.single)

        myNumOfNeighb[myNumOfNeighb == 0] = 1
        myIm = temp_im / myNumOfNeighb

    # Restore original values at masked locations
    myIm[myMask_neg] = argIm[myMask_neg]
    return myIm
