import numpy as np

def bmCol(a):
    """
    % out = bmCol(a)
    %
    % This function returns the input data as a column vector.
    % This is the same as doing:
    % temp = a;
    % out = a(:);
    % But allows to do it in one line and thus nest in other function calls
calls.
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
    %   a (array): Input data
    %
    % Returns:
    %   out (column vector): Data (a) as column vector
    """
    return np.asarray(a).reshape(-1, 1)
