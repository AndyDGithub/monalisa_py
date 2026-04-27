import numpy as np
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape from arrayUtility module

def bmVarargin_false(varargin):
    varargout = []
    nargout = len(varargin)

    for i in range(nargout):
        if not varargin[i]:
            varargout.append(False)
        else:
            varargout.append(varargin[i])

    return np.array(varargout)
