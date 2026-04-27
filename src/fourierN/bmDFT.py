import numpy as np

def bmDFT(f, x, *varargin):
    # parse varargin
    nZero = 0
    nDim = 1
    gridType = None
    if len(varargin) >= 1:
        nZero = varargin[0]
    if len(varargin) >= 2:
        nDim = varargin[1]
    if len(varargin) >= 3:
        gridType = varargin[2]
