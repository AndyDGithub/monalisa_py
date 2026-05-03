from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty, single, size
from porting.lib.utils import ndims
from src.varargin.bmVarargin import bmVarargin

from src.image123.bmImConv_inMask_byShiftList import circshift

def bmImConv_byShiftList(argIm, argShiftList, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # Translated from MATLAB logic
    myKernelVal, nIter = bmVarargin(varargin)
    
    if isempty(myKernelVal):
        myKernelVal = np.ones((size(argShiftList, 0), 1))
    
    if isempty(nIter):
        nIter = 1
    
    argSize = size(argIm)
    mySize = argSize[:]
    out_1 = single(argIm)
    
    if ndims(out_1) == 2:
        if (mySize[0] == 1) or (mySize[1] == 1):
            out_1 = out_1.flatten()
    
    mySize = size(out_1)
    out_2 = np.zeros(mySize, dtype=np.single)
    
    nShift = size(argShiftList, 0)
    
    for i in range(nIter):
        for j in range(nShift):
            out_2 += circshift(out_1, argShiftList[j, :]) * myKernelVal[j, 
0]
        
        out_1 = out_2 / nShift
        out_2 = np.zeros(argSize, dtype=np.single)
    
    out_1 = reshape(out_1, argSize)
    
    return out_1
