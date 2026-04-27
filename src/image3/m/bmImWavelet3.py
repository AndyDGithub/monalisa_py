from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty


def bmImWavelet3(x, n_u, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # We use the function 'dwt3' which performs a single-level 3D discrete
    # wavelet transform.
    # 
    # We use the wavelet_type 'sym4' by default.
    # 
    # We use periodic image extension.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: wavelet_type = bmVarargin(varargin);
    # MATLAB: if isempty(wavelet_type)
    # MATLAB: wavelet_type = 'sym4'; % magic
    # MATLAB: end
    # MATLAB: n_u = n_u(:)';
    # MATLAB: x = bmBlockReshape(x, n_u);
    # MATLAB: [cA, cH, cV, cD] = dwt3(x, wavelet_type, 'mode', 'per');
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    cA = None
    cH = None
    cV = None
    cD = None
    return cA, cH, cV, cD
