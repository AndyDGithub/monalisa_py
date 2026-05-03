from src.image123.bmImReshape import bmImReshape
import numpy as np
from third_part.matlab_compat.matlab_native import single
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Import bmBlockReshape from the given path

try:
    from src.image1.mex.bmImLaplacian1.bmImLaplacian1_mex import bmImLaplacian1_mex
except Exception:
    def bmImLaplacian1_mex(*_args, **_kwargs):
        raise NotImplementedError("Native backend 'bmImLaplacian1_mex' is unavailable. Run compile_mex_for_monalisa() to build MEX binaries first.")

try:
    from src.image2.mex.bmImLaplacian2.bmImLaplacian2_mex import bmImLaplacian2_mex
except Exception:
    def bmImLaplacian2_mex(*_args, **_kwargs):
        raise NotImplementedError("Native backend 'bmImLaplacian2_mex' is unavailable. Run compile_mex_for_monalisa() to build MEX binaries first.")

try:
    from src.image3.mex.bmImLaplacian3.bmImLaplacian3_mex import bmImLaplacian3_mex
except Exception:
    def bmImLaplacian3_mex(*_args, **_kwargs):
        raise NotImplementedError("Native backend 'bmImLaplacian3_mex' is unavailable. Run compile_mex_for_monalisa() to build MEX binaries first.")


from src.sparseMat.m.bmSparseMat_vec import int32

def bmImLaplacian(argIm):
    # Get original size
    argSize = np.shape(argIm)

    # Get dimension and size of input data (also get data as column vector if
    # argIm is 1D)
    [argIm, imDim, _, sx, sy, sz] = bmImReshape(argIm)

    # Check if the data is real
    real_flag = np.isreal(argIm).all()

    # Set the correct format for the variables
    argIm     = single(argIm)
    sx        = int32(sx)
    sy        = int32(sy)
    sz        = int32(sz)

    if imDim == 1:
        if real_flag:
            out = bmImLaplacian1_mex(sx, argIm)

        else:
            out_real = bmImLaplacian1_mex(sx, np.real(argIm))
            out_imag = bmImLaplacian1_mex(sx, np.imag(argIm))
            out = complex(out_real, out_imag)

    elif imDim == 2:
        if real_flag:
            out = bmImLaplacian2_mex(sx, sy, argIm)

        else:
            out_real = bmImLaplacian2_mex(sx, sy, np.real(argIm))
            out_imag = bmImLaplacian2_mex(sx, sy, np.imag(argIm))
            out = complex(out_real, out_imag)

    elif imDim == 3:
        if real_flag:
            # Efficiently compute the Laplacian of a real 3D data in c++
            out = bmImLaplacian3_mex(sx, sy, sz, argIm)

        else:
            # Efficiently compute the Laplacian of real 3D data in c++,
            # repeat for the imaginary part
            out_real = bmImLaplacian3_mex(sx, sy, sz, np.real(argIm))
            out_imag = bmImLaplacian3_mex(sx, sy, sz, np.imag(argIm))

            # Combine results in a complex output array
            out = complex(out_real, out_imag)

    # Reshape to original size
    out = np.reshape(out, argSize)
    return out
