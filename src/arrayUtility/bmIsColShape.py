import numpy as np

def bmIsColShape(x, N_u):
    """
% out = bmIsColShape(x, N_u)
%
% This function checks if the data in array x is in the column format, 
% i.e., contains a column vector for each channel.
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
%   x (array): Array of which the format should be tested.
%   N_u (list): Size of the data of one channel in x.
%
% Returns:
%   out (logical): 1 if x is in column format, 0 if not.
    """
    # Number of channels
    nCh = x.size // np.prod(N_u)
    # Desired shape in column format
    myColSize = (int(np.prod(N_u)), nCh)
    # Return boolean indicating shape match
    return x.shape == myColSize
