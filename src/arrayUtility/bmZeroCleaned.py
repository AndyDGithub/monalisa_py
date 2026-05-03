import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmZeroCleaned(argA):
    """Remove zeros from an array.

    MATLAB source:
    function out = bmZeroCleaned(argA)
        out = argA(:);
        out(out == 0) = [];
    end
    """
    # Flatten the input array
    out = np.asarray(argA).ravel()
    # Remove zero elements
    out = out[out != 0]
    return out
