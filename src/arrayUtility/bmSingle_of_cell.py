import numpy as np


def bmSingle_of_cell(arg_cell):
    if isinstance(arg_cell, list):
        arg_cell = np.array(arg_cell, dtype=object)
    out = np.empty(arg_cell.shape, dtype=object)
    for i in range(arg_cell.size):
        out.ravel()[i] = np.asarray(arg_cell.ravel()[i]).astype("float32")
    return out
