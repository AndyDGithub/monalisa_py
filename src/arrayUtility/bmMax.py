# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np


def bmMax(x):
    """
    Compute the maximum value in a list or array.

    This function replicates MATLAB's bmMax: if *x* is a cell (list of
    arrays), it returns the maximum value among all elements in all cells.
    Otherwise it returns the maximum of the array.
    """
    if isinstance(x, list):
        m_list = [np.max(np.asarray(item).ravel()) for item in x]
        return np.max(m_list)
    elif isinstance(x, np.ndarray) and x.dtype == object:
        m_list = [np.max(np.asarray(item).ravel()) for item in x]
        return np.max(m_list)
    else:
        return np.max(np.asarray(x))
