from src.fourier2.bcaNeith_interpolatekSpace2 import bcaNeith_interpolatekSpace
from src.fourier2.bcaNeith_interpolatorExtraction2 import bcaNeith_interpolatorExtraction
from src.fourier2.bcaNeith_kernelTypeExtraction2 import bcaNeith_kernelTypeExtraction
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Import statement for missing module

def bcaNeith2(kspace, calib, kern):
    padsize = (kern - 1) // 2;  # Padding the k-space first so that edge of the

    # Apply padding to k-space
    kspace_padded = bmBlockReshape(kspace, [padsize, 0], 0)

    # Call the main functionality functions one by one
    kern_types = bcaNeith_kernelTypeExtraction(kspace_padded, kern)
    interp_kerns = bcaNeith_interpolatorExtraction(calib, kern_types, kern)
    res = bcaNeith_interpolatekSpace(kspace_padded, interp_kerns, kern_types, kern)

    # Remove the padding to retain original size
    res = np.delete(res, np.s_[0:padsize[0],:], axis=0)
    res = np.delete(res, np.s_[:, 0:padsize[0]], axis=1)
    res = np.delete(res, np.s_[range(kern-1, res.shape[0]), :], axis=0)
    res = np.delete(res, np.s_[:, range(kern-1, res.shape[1])], axis=1)

    return res
