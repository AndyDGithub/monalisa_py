from __future__ import annotations
from third_part.matlab_compat.matlab_native import single, size
from porting.lib.utils import imag, int32, real


def bmImCrossMean(argIm):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: argSize = size(argIm);
    # MATLAB: [argIm, imDim, ~, sx, sy, sz] = bmImReshape(argIm);
    # MATLAB: real_flag = isreal(argIm);
    # MATLAB: argIm     = single(argIm);
    # MATLAB: sx        = int32(sx);
    # MATLAB: sy        = int32(sy);
    # MATLAB: sz        = int32(sz);
    # MATLAB: if imDim == 1
    # MATLAB: error('Case not implemented. ');
    # MATLAB: return;
    # MATLAB: elseif imDim == 2
    # MATLAB: if real_flag
    # MATLAB: out = bmImCrossMean2_mex(sx, sy, argIm);
    # MATLAB: else
    # MATLAB: out_real = bmImCrossMean2_mex(sx, sy, real(argIm));
    # MATLAB: out_imag = bmImCrossMean2_mex(sx, sy, imag(argIm));
    # MATLAB: out = complex(out_real, out_imag);
    # MATLAB: end
    # MATLAB: elseif imDim == 3
    # MATLAB: if real_flag
    # MATLAB: out = bmImCrossMean3_mex(sx, sy, sz, argIm);
    # MATLAB: else
    # MATLAB: out_real = bmImCrossMean3_mex(sx, sy, sz, real(argIm));
    # MATLAB: out_imag = bmImCrossMean3_mex(sx, sy, sz, imag(argIm));
    # MATLAB: out = complex(out_real, out_imag);
    # MATLAB: end
    # MATLAB: end
    # MATLAB: out = reshape(out, argSize);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out = None
    return out
