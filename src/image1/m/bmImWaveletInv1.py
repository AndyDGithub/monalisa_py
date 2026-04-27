from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty


def bmImWaveletInv1(cA, cD, n_u, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # We use the function 'idwt' which performs an inverse single-level 1D
    # discrete wavelet transform.
    # 
    # We use the wavelet_type 'sym4' by default.
    # 
    # We use periodic extension.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: wavelet_type = bmVarargin(varargin);
    # MATLAB: if isempty(wavelet_type)
    # MATLAB: wavelet_type = 'sym4'; % magic
    # MATLAB: end
    # MATLAB: cA = cA(:);
    # MATLAB: cD = cD(:);
    # MATLAB: x = idwt(cA, cD, wavelet_type, 'mode', 'per');
    # MATLAB: x = bmBlockReshape(x, n_u);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    x = None
    return x
