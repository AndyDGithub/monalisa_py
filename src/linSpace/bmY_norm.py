import numpy as np
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from src.varargin.bmVarargin import bmVarargin

def bmY_norm(y, d_n, varargin):
    # n = bmY_norm(y, d_n, varargin)
    # 
    # This function computes the weighted norm of the data y with the volume
    # elements d_n. The norm is computed for every channel.
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
    # y (array): The data containing datapoints per channel.
    # d_n (array): The volume elements for every datapoint. Can be a scalar
    # taken for every datapoint, or can have different values for different
    # channels.
    # varargin{1}: Flag; collapses the output into a single value if true.
    # Another norm is calculated across channels to receive this value.
    # Default value is false.
    # 
    # Returns:
    # n (list): The norms for every channel computed over the datapoints.
    # Only a scalar if y only contains one channel or the optional flag is
    # true. Row or column vector depending on y -> if size(y,2) = nCh then
    # size(n,2) = nCh and n is a row vector.

    # Extract optional arguments
    collapse_flag = bmVarargin(varargin)
    
    # Set default value
    if not collapse_flag:
        collapse_flag = False
        
    # Throw an error if y has more than 2 dimensions
    if y.ndim > 2:
        raise ValueError("This function is for 2Dim arrays only.")

    # Reshape (and resize if necessary) d_n to match the size of y
    d_n = bmY_ve_reshape(d_n, np.shape(y))
    
    # Calculate the weighted norm along the datapoints (1 norm per channel)
    if y.shape[0] > y.shape[1]:
        # Each column is a channel
        n = np.sqrt(np.abs(np.sum(np.conj(y) * (y * d_n), axis=1)))
    else:
        # Each row is a channel
        n = np.sqrt(np.abs(np.sum(np.conj(y) * (y * d_n), axis=0)))
    
    # Collapse the norms into a single norm instead of having norms for each
    # channel
    if collapse_flag:
        n = np.sqrt(np.sum(n ** 2))

    return n
