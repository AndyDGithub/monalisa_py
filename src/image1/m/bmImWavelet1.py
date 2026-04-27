from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty


def bmImWavelet1(x, n_u, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # We use the function 'dwt' which performs a single-level 1D discrete
    # wavelet transform.
    # 
    # We use the wavelet_type 'sym4' by default.
    # 
    # We use periodic extension.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: wavelet_type = bmVarargin(varargin);
    # MATLAB: if isempty(wavelet_type)
    # MATLAB: wavelet_type = 'sym4'; % magic
    # MATLAB: end
    # MATLAB: n_u = n_u(:)';
    # MATLAB: x = bmBlockReshape(x, n_u);
    # MATLAB: [cA, cD] = dwt(x, wavelet_type, 'mode', 'per');
    # MATLAB: cA = cA(:);
    # MATLAB: cD = cD(:);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    cA = None
    cD = None
    return cA, cD
