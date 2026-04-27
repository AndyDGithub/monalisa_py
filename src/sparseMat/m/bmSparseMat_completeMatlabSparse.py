import numpy as np
from scipy import sparse

def bmSparseMat_completeMatlabSparse(argSparse, mySize):
    # mySparse = bmSparseMat_completeMatlabSparse(argSparse, mySize)
    #
    # This function completes the sparse matrix to match the size given with
    # the second argument. If the given size is bigger than the size of
    # argSparse, argSparse is increased by adding all zero sparse matrices. If
    # the given size is smaller or equal, no changes are done.
    #
    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    #
    # Parameters:
    # argSparse (sparse matrix): The sparse matrix to be completed.
    # mySize (list): 1D array containing the size (column, row) that the
    # sparse matrix (argSparse) has to have at a minimum.
    #
    # Results:
    # mySparse (sparse matrix): argSparse padded with all zero sparse
    # matrices.

    mySparse = argSparse
    a1 = int(np.shape(mySparse)[1])
    a2 = int(np.shape(mySparse)[0])
    mySize = np.array(mySize).ravel().T
    b1 = int(mySize[0, 0])
    b2 = int(mySize[0, 1])

    if b1 > a1:
        # Create all zero sparse matrix
        temp_sparse = sparse.csr_matrix((b1 - a1, a2))
        # Concatenate to have a1 == b1
        mySparse = sparse.hstack([mySparse, temp_sparse], format='csr')

    if b2 > a2:
        # Create all zero sparse matrix
        temp_sparse = sparse.csr_matrix((a1, b2 - a2))
        # Concatenate to have a2 == b2
        mySparse = sparse.vstack([mySparse, temp_sparse], format='csr')

    return mySparse
