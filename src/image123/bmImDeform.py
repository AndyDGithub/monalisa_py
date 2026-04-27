from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.fourier1.bmDFT1 import bmDFT1
from src.fourier2.bmDFT2 import bmDFT2
from src.fourier3.bmDFT3 import bmDFT3
from src.sparseMat.m.bmSparseMat_vec import bmSparseMat_vec

from src.arrayUtility.bmIsBlockShape import bmIsBlockShape
from src.fourier1.bmIDF1 import bmIDF1
from src.fourier2.bmIDF2 import bmIDF2
from src.fourier3.bmIDF3 import bmIDF3
import numpy as np

def bmImDeform(Tu, x, n_u, K):
    if Tu.size == 0:
        x_out = x
        return x_out

    imDim   = np.shape(n_u, 1)
    x_out   = bmColReshape(x, n_u)
    x_out   = bmSparseMat_vec(Tu, x_out, "omp", "complex", False)

    if K is not None:
        K       = bmColReshape(K, n_u)
        Fx = []

        if imDim == 1:
            Fx = bmDFT1(x_out, n_u, 1./n_u)
        elif imDim == 2:
            Fx = bmDFT2(x_out, n_u, 1./n_u)
        elif imDim == 3:
            Fx = bmDFT3(x_out, n_u, 1./n_u)

        Fx = np.multiply(Fx, K)

        if imDim == 1:
            x_out = bmIDF1(Fx, n_u, 1./n_u)
        elif imDim == 2:
            x_out = bmIDF2(Fx, n_u, 1./n_u)
        elif imDim == 3:
            x_out = bmIDF3(Fx, n_u, 1./n_u)

    if bmIsBlockShape(x, n_u):
        x_out = bmBlockReshape(x_out, n_u)

    return x_out
