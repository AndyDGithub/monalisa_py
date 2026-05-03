import numpy as np


def bmSingle_of_cell(arg_cell):
    """Convert a cell-like container to an array of single-precision floats
floats.
    MATLAB reference: bmSingle_of_cell.m
    """
    # out = cell(size(arg_cell));
    arg_arr = np.asarray(arg_cell)
    out = np.empty_like(arg_arr, dtype=np.float32)

    # for i = 1:length(arg_cell(:))
    for idx, val in np.ndenumerate(arg_arr):
        #     out{i} = single(arg_cell{i});
        out[idx] = np.float32(val)

    # end
    return out

# End of file
