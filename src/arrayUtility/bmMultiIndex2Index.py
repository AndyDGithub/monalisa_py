import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmMultiIndex2Index(argMultiInd, argSize):
    """Converts multi-index to linear index.

    Parameters
    ----------
    argMultiInd : array_like
        Multi-dimensional index.
    argSize : array_like
        Size of the array in each dimension.

    Returns
    -------
    outInd : int
        Linear index corresponding to the multi-index.
    """
    my_multi_ind = np.array(argMultiInd, dtype=int).ravel() - 1
    my_size = np.array(argSize, dtype=int).ravel()
    L = len(my_size)
    out_ind = my_multi_ind[0]
    for i in range(1, L):
        out_ind += my_multi_ind[i] * np.prod(my_size[:i])
    out_ind += 1
    return out_ind
