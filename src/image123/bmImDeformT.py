from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.fourier1.bmDFT1_conjTrans import bmDFT1_conjTrans
from src.fourier2.bmDFT2_conjTrans import bmDFT2_conjTrans
from src.fourier3.bmDFT3_conjTrans import bmDFT3_conjTrans
from src.fourier1.bmIDF1_conjTrans import bmIDF1_conjTrans
from src.fourier2.bmIDF2_conjTrans import bmIDF2_conjTrans
from src.fourier3.bmIDF3_conjTrans import bmIDF3_conjTrans
from src.sparseMat.m.bmSparseMat_vec import bmSparseMat_vec
import numpy as np

from src.image123.bmImResize import bmIsBlockShape

def bmImDeformT(Tut, x, n_u, K):
    if Tut is None:
        x_out = x
        return x_out

    x_out   = bmColReshape(x, n_u)
    imDim   = np.shape(n_u.ravel(), 1)
    if not (K is None):
        K       = bmColReshape(K, n_u)
        Fx = []
        if imDim == 1:
            Fx = bmIDF1_conjTrans(x_out, n_u, 1./n_u)
        elif imDim == 2:
            Fx = bmIDF2_conjTrans(x_out, n_u, 1./n_u)
        elif imDim == 3:
            Fx = bmIDF3_conjTrans(x_out, n_u, 1./n_u)
        Fx = Fx * K

        if imDim == 1:
            x_out = bmDFT1_conjTrans(Fx, n_u, 1./n_u)
        elif imDim == 2:
            x_out = bmDFT2_conjTrans(Fx, n_u, 1./n_u)
        elif imDim == 3:
            x_out = bmDFT3_conjTrans(Fx, n_u, 1./n_u)

    x_out = bmSparseMat_vec(Tut, x_out, "omp", "complex", False)
    if bmIsBlockShape(x, n_u):
        x_out = bmBlockReshape(x_out, n_u)

    return x_out
