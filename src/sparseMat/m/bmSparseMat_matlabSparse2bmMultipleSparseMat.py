from third_part.matlab_compat.numpy_utils import histcounts
import numpy as np

from src.sparseMat.m.bmSparseMat_vec import int32

def t(ms, i, matlabSparseMat, N_u, d_u, kernelType, nWin, kernelParam):
    size_1 = np.shape(matlabSparseMat, 1)
    size_2 = np.shape(matlabSparseMat, 2)
    matlabSparseMat = matlabSparseMat.T
    [ind_1, ind_2, m_val] = np.where(matlabSparseMat != 0)
    r_nJump = histcounts(ind_2, np.arange(size_1 + 1) - 0.5)[0]
    ms.r_size[i]            = int32(size_2)
    ms.l_size[i]            = int32(size_1)
    ms.l_nJump[i]           = int32(size_1)
    ms.r_nJump[i]           = r_nJump
    ms.r_ind[i]             = ind_1
    ms.m_val[i]             = np.single(m_val)
    ms.N_u[i]               = int32(N_u)
    ms.d_u[i]               = np.single(d_u)
    ms.kernel_type[i]       = kernelType
    ms.nWin[i]              = int32(nWin)
    ms.kernelParam[i]       = np.single(kernelParam)
    ms.block_type[i]        = "void"
    ms.type[i]              = "matlab_ind"
    ms.l_squeeze_flag[i]    = False

def bmSparseMat_matlabSparse2bmMultipleSparseMat(ms, i, matlabSparseMat, N_u, d_u, kernelType, nWin, kernelParam):
    t(ms, i, matlabSparseMat, N_u, d_u, kernelType, nWin, kernelParam)
