# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmCsvReshape(argArray, argSize):
    # Reshape a 2D array into a 3D array with the specified size.
    #
    # Parameters:
    #     argArray (np.ndarray): Input 2D array.
    #     argSize (tuple or list): 3-element sequence specifying shape
    #         (rows, cols, slices).
    #
    # Returns:
    #     np.ndarray: Reshaped 3D array.
    s1, s2, s3 = argSize
    if argArray.ndim != 2:
        raise ValueError("argArray must be 2D")
    if argArray.shape[0] != s1 * s3 or argArray.shape[1] != s2:
        raise ValueError("argArray shape does not match argSize")
    out = np.empty((s1, s2, s3), dtype=argArray.dtype)
    for i in range(s3):
        rows = argArray[i * s1:(i + 1) * s1, :]
        out[:, :, i] = rows
    return out


# MATLAB reference:
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
#
# function out = bmCsvReshape(argArray, argSize)
#
# out = zeros(argSize);
# for i = 1:length(argArray(:))/argSize(1)/argSize(2)
#     out(:,:,i) = argArray((i-1)*argSize(1)+1:i*argSize(1), :);
# end
# out = reshape(out, argSize);
# end %end of function
