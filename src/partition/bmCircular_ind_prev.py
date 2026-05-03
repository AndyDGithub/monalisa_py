import numpy as np

# % Bastien Milani
# % CHUV and UNIL
# % Lausanne - Switzerland
# % May 2023
#
# % nRank is the total number of index position. It is a natural number.  
# %
# % ind_curr is the current (input) index. 
# %
# % index_mode must be 'reduced' or 'natural'. 

def bmCircular_ind_prev(nRank, ind_curr, index_mode):
    """
    Return the previous index in a circular sequence.

    Parameters
    ----------
    nRank : int
        Total number of index positions (natural number).
    ind_curr : int
        Current index (natural or reduced depending on index_mode).
    index_mode : str
        Either 'natural' or 'reduced'. In 'natural' mode the input and outp
output
        indices are 1-based. In 'reduced' mode they are 0-based.

    Returns
    -------
    int
        The previous index, in the same mode as the input.
    """
    if index_mode == 'natural':
        ind_curr = ind_curr - 1  # Convert to reduced index

    ind_prev = np.mod(ind_curr - 1 + nRank, nRank)  # Reduced index

    if index_mode == 'natural':
        ind_prev = ind_prev + 1  # Convert back to natural index

    return int(ind_prev)
