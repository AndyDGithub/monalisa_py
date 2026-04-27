import numpy as np
from src.image123.bmImReshape import bmImReshape

from src.sparseMat.m.bmSparseMat_vec import int32

def bmImGradient(argIm):
    out_x = []
    out_y = []
    out_z = []

    argIm, imDim, _, sx, sy, sz = bmImReshape(argIm)
    real_flag = np.isrealobj(argIm)
    argIm     = np.array(argIm, dtype=np.float32)
    sx        = int32(sx)
    sy        = int32(sy)
    sz        = int32(sz)

    if imDim == 1:
        raise ValueError('Case not implemented. ')

    elif imDim == 2:
        if real_flag:
            [out_x, out_y] = bmImGradient2_mex(sx, sy, argIm)
        else:
            [out_x_real, out_y_real] = bmImGradient2_mex(sx, sy, np.real(argIm))
            [out_x_imag, out_y_imag] = bmImGradient2_mex(sx, sy, np.imag(argIm))
            out_x = complex(out_x_real, out_x_imag)
            out_y = complex(out_y_real, out_y_imag)

    elif imDim == 3:
        if real_flag:
            [out_x, out_y, out_z] = bmImGradient3_mex(sx, sy, sz, argIm)
        else:
            [out_x_real, out_y_real, out_z_real] = bmImGradient3_mex(sx, sy, sz, np.real(argIm))
            [out_x_imag, out_y_imag, out_z_imag] = bmImGradient3_mex(sx, sy, sz, np.imag(argIm))
            out_x = complex(out_x_real, out_x_imag)
            out_y = complex(out_y_real, out_y_imag)
            out_z = complex(out_z_real, out_z_imag)

    if imDim == 2:
        imGradient = np.concatenate((out_x, out_y), axis=0)
    elif imDim == 3:
        imGradient = np.concatenate((out_x, out_y, out_z), axis=0)

    return imGradient
