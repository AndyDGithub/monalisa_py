import numpy as np
from importlib import import_module
from typing import Callable, Any
from src.image123.bmImReshape import bmImReshape


def _missing_backend(name: str) -> Callable[..., Any]:
    def _raise(*_args, **_kwargs):
        raise NotImplementedError(
            f"Native backend '{name}' is unavailable. "
            "Run compile_mex_for_monalisa() to build MEX binaries first."
        )
    return _raise


def _load_backend(module_path: str, symbol: str) -> Callable[..., Any]:
    try:
        module = import_module(module_path)
        return getattr(module, symbol)
    except Exception:
        return _missing_backend(symbol)


bmImGradient2_mex = _load_backend(
    "src.image2.mex.bmImGradient2.bmImGradient2_mex",
    "bmImGradient2_mex",
)
bmImGradient3_mex = _load_backend(
    "src.image3.mex.bmImGradient3.bmImGradient3_mex",
    "bmImGradient3_mex",
)


from src.sparseMat.m.bmSparseMat_vec import int32

# bmImGradient2_mex is cpp file in this directory : src\image2\mex\bmImGradient2\bmImGradient2_mex.cpp

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
            out_x = out_x_real + 1j * out_x_imag
            out_y = out_y_real + 1j * out_y_imag

    elif imDim == 3:
        if real_flag:
            [out_x, out_y, out_z] = bmImGradient3_mex(sx, sy, sz, argIm)
        else:
            [out_x_real, out_y_real, out_z_real] = bmImGradient3_mex(sx, sy, sz, np.real(argIm))
            [out_x_imag, out_y_imag, out_z_imag] = bmImGradient3_mex(sx, sy, sz, np.imag(argIm))
            out_x = out_x_real + 1j * out_x_imag
            out_y = out_y_real + 1j * out_y_imag
            out_z = out_z_real + 1j * out_z_imag

    if imDim == 2:
        imGradient = np.concatenate((out_x, out_y), axis=0)
    elif imDim == 3:
        imGradient = np.concatenate((out_x, out_y, out_z), axis=0)

    return imGradient
