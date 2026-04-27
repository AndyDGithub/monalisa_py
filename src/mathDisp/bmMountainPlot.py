from __future__ import annotations
from third_part.matlab_compat.matlab_native import double, length, size
from porting.lib.utils import size


def t(M, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # This function take an n-times-m matrix M as argument and plot the
    # corresponding surfaceplot.
    # figure
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: M = double(M);
    # MATLAB: if length(varargin) > 1
    # MATLAB: x = varargin{1};
    # MATLAB: y = varargin{2};
    # MATLAB: else
    # MATLAB: [iMax, jMax] = size(M);
    # MATLAB: x = 1:iMax;
    # MATLAB: y = 1:jMax;
    # MATLAB: end
    # MATLAB: [X, Y]  = ndgrid(x, y);
    # MATLAB: mesh(X, Y, M, 'FaceAlpha', 0)
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    bmMountainPlo = None
    return bmMountainPlo

# Auto-generated entrypoint alias for import compatibility
bmMountainPlot = t
