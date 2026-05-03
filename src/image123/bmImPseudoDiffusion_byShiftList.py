from __future__ import annotations
import numpy as np

from src.image123.bmImConv_inMask_byShiftList import isempty, single

def bmImPseudoDiffusion_byShiftList(argIm, argShiftList, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # Convert input to float and squeeze it
    argIm = np.squeeze(single(argIm))
    
    # Handle optional nIter argument
    if not isempty(varargin) and len(varargin) > 0:
        nIter = int(varargin[0])
    else:
        nIter = 1
    
    # Initialize output as a copy of input image
    out_1 = argIm.copy()
    myDim = out_1.ndim
    
    # If the image is 1D, reshape it to be 2D for processing
    if myDim == 1:
        out_1 = out_1[:, np.newaxis]
    
    # Get the size of the image and prepare masks and variables
    argSize = out_1.shape
    nShift = len(argShiftList)
    
    # Perform the convolution operation over specified iterations
    for i in range(nIter):
        myZeroMask = (out_1 == 0)
        myZeroMask = myZeroMask.reshape(argSize)
        myNonZeroMask = np.logical_not(myZeroMask)
        
        out_2 = np.zeros_like(out_1, dtype=np.float32)
        myNumOfNonZero = np.zeros_like(out_1, dtype=np.float32)
        
        for j in range(nShift):
            out_2 += np.roll(out_1, argShiftList[j], axis=(0, 1))
            myNumOfNonZero += np.where(myNonZeroMask, 1.0, 0.0)
        
        # Handle division by zero
        myNumOfNonZero[myNumOfNonZero == 0] = 1.0
        
        out_1 = out_2 / myNumOfNonZero
    
    return out_1
