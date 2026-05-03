import numpy as np

"""
function out = bmColReshape(argIn, argSize)
% out = bmColReshape(argIn, argSize)
%
% This function reshapes the data into column vectors, with each vector
% containing data of one channel. The data can be given in an array or cell
cell
% array. In case of a cell array, the arrays in each cell are reshaped.
reshaped.
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
%   argIn (array / cell array): Data that should be reshaped.
%   argSize (list): Size of the data of one channel. Used to calculate the
%   number of channels.
%
% Results:
%   out (array / cell array): The data reshaped into column vectors. The
%   type depends on the input.
"""

def bmColReshape(argIn, argSize):
    """
    Reshape data into column vectors, one per channel.

    Parameters
    ----------
    argIn : array-like or list of array-like
        Data to reshape. A list is interpreted as a cell array, and each
        element is processed recursively.
    argSize : array-like
        Size of the data for a single channel. Its product determines the
        number of points per channel.

    Returns
    -------
    out : array or list of arrays
        Reshaped data. If the input was a list, the output is a list with
        the same structure; otherwise an ndarray of shape (nPts, nCh).
    """
    # If argIn is a list, treat it as a cell array and recurse.
    if isinstance(argIn, list):
        return [bmColReshape(item, argSize) for item in argIn]

    # If argIn is a NumPy array with object dtype, treat each element as a
    # sub-array (e.g. array of arrays) and recurse element-wise.
    if isinstance(argIn, np.ndarray) and argIn.dtype == object:
        out = np.empty_like(argIn)
        for i, item in enumerate(argIn.ravel()):
            out.ravel()[i] = bmColReshape(item, argSize)
        return out

    # Convert to a NumPy array for numeric operations.
    argIn = np.asarray(argIn)

    # Number of points per channel.
    nPt = int(np.prod(np.array(argSize).ravel()))

    # Number of channels. The input is expected to contain an integer
    # number of points that is a multiple of nPt.
    nCh = argIn.size // nPt

    # Reshape into (nPt, nCh) where each column is a channel.
    return argIn.reshape(nPt, nCh)
