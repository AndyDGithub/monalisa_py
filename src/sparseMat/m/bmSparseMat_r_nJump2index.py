import numpy as np

# bmSparseMat_r_nJump2index
# Authors:
#   Bastien Milani
#   CHUV and UNIL
#   Lausanne - Switzerland
#   May 2023

# bmSparseMat_r_nJump2index
# --------------------------------------------
# This function expands the input array into indices based on the number of
of
# grid points repeated for each point, using a mex function to efficientl
efficiently
# do this in c++.
#
# Authors:
#   Bastien Milani
#   CHUV and UNIL
#   Lausanne - Switzerland
#   May 2023
#
# Parameters:
#   r_nJump (array): Contains for each point the number of points in the
#   second dimension (grid), the number of indices jumped in a flattened
#   array to get to the next point.
#
# Returns:
#   out (array): Contains a list that repeats r_nJump(index) times the
#   corresponding index in r_nJump for every point / index and is of size
#   sum(r_nJump).
#
# Examples:
#   out = bmSparseMat_r_nJump2index([3, 1, 0, 2])
#       out = [1, 1, 1, 2, 4, 4]
#
#   out = bmSparseMat_r_nJump2index([0, 0, 0, 10, 0, 10])
#       out = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
#
# Notes:
#   bmSparseMat_r_nJump2index is the inverse operation of
#   histcounts(out, (1:size(r_nJump, 2) + 1) - 0.5)

def bmSparseMat_r_nJump2index(r_nJump):
    """
    Expand an array of jump counts into repeated indices.
    """
    r_nJump = np.asarray(r_nJump, dtype=np.int64).ravel()
    l_size = r_nJump.size
    out = np.repeat(np.arange(1, l_size + 1, dtype=np.int64), r_nJump)
    return out
