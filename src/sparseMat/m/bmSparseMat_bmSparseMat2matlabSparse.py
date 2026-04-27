from third_part.matlab_compat.matlab_native import double
import numpy as np
from src.sparseMat.m.bmSparseMat_r_nJump2index import bmSparseMat_r_nJump2index

def bmSparseMat_bmSparseMat2matlabSparse(a):
    if not (a.type == 'matlab_ind'):
        raise ValueError("The type of the bmSparseMat must be 'matlab_ind'. ")

    size_1 = double(a.l_size)
    size_2 = double(a.r_size)
    n_jump = double(a.r_nJump)
    r_ind  = double(a.r_ind)
    m_val  = double(a.m_val)
    l_ind  = double(bmSparseMat_r_nJump2index(n_jump))

    b = np.sparse((r_ind, l_ind, m_val), (size_1, size_2))
    b = b.T

    if b.shape[1] < a.r_size:
        temp_sparse = np.sparse((np.arange(b.shape[0]), np.zeros(a.r_size - b.shape[1])), (b.shape[1], a.r_size - b.shape[1]))
        b = np.concatenate((b, temp_sparse), axis=1)

    if b.shape[0] < a.l_size:
        temp_sparse = np.sparse((np.zeros(a.l_size - b.shape[0]), np.arange(b.shape[1])), (a.l_size - b.shape[0], b.shape[1]))
        b = np.concatenate((b, temp_sparse), axis=0)

    return b
