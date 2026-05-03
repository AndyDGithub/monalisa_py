from third_part.matlab_compat.matlab_native import single
import numpy as np
from src.image123.bmImReshape import bmImReshape

try:
    from src.image2.mex.bmImCrossMean2_omp.bmImCrossMean2_omp_mex import bmImCrossMean2_omp_mex
except Exception:
    def bmImCrossMean2_omp_mex(*_args, **_kwargs):
        raise NotImplementedError("Native backend 'bmImCrossMean2_omp_mex' is unavailable. Run compile_mex_for_monalisa() to build MEX binaries first.")

try:
    from src.image3.mex.bmImCrossMean3_omp.bmImCrossMean3_omp_mex import bmImCrossMean3_omp_mex
except Exception:
    def bmImCrossMean3_omp_mex(*_args, **_kwargs):
        raise NotImplementedError("Native backend 'bmImCrossMean3_omp_mex' is unavailable. Run compile_mex_for_monalisa() to build MEX binaries first.")


from src.sparseMat.m.bmSparseMat_vec import int32

def bmImCrossMean_omp(argIm):
    argSize = np.shape(argIm)
    [argIm, imDim, imSize, sx, sy, sz] = bmImReshape(argIm)
    real_flag = np.isreal(argIm)
    argIm     = single(argIm)
    sx        = int32(sx)
    sy        = int32(sy)
    sz        = int32(sz)
    nBlockPerThread = int32(max(imSize.ravel()))

    if imDim == 1:
        raise ValueError('Case not implemented.')

    elif imDim == 2:
        if real_flag:
            out = bmImCrossMean2_omp_mex(sx, sy, argIm, nBlockPerThread)
        else:
            out_real = bmImCrossMean2_omp_mex(sx, sy, np.real(argIm), nBlockPerThread)
            out_imag = bmImCrossMean2_omp_mex(sx, sy, np.imag(argIm), nBlockPerThread)
            out = complex(out_real, out_imag)

    elif imDim == 3:
        if real_flag:
            out = bmImCrossMean3_omp_mex(sx, sy, sz, argIm, nBlockPerThread)
        else:
            out_real = bmImCrossMean3_omp_mex(sx, sy, sz, np.real(argIm), nBlockPerThread)
            out_imag = bmImCrossMean3_omp_mex(sx, sy, sz, np.imag(argIm), nBlockPerThread)
            out = complex(out_real, out_imag)

    out = np.reshape(out, argSize)
    return out
