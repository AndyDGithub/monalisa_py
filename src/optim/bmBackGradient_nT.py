from __future__ import annotations
from third_part.matlab_compat.matlab_native import size


def bmBackGradient_nT(x, n_u, dX_u, n):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: imDim   = size(n_u(:), 1);
    # MATLAB: n_u     = n_u(:)';
    # MATLAB: dX_u    = dX_u(:)';
    # MATLAB: myShift = zeros(1, imDim);
    # MATLAB: myShift(1, n) = 1;
    # MATLAB: if imDim == 1
    # MATLAB: x = reshape(x, [n_u, 1]);
    # MATLAB: g = x;
    # MATLAB: if n == 1
    # MATLAB: g(1, 1) = 0;
    # MATLAB: end
    # MATLAB: elseif imDim == 2
    # MATLAB: x = reshape(x, n_u);
    # MATLAB: g = x;
    # MATLAB: if n == 1
    # MATLAB: g(1, :) = 0;
    # MATLAB: elseif n == 2
    # MATLAB: g(:, 1) = 0;
    # MATLAB: end
    # MATLAB: elseif imDim == 3
    # MATLAB: x = reshape(x, n_u);
    # MATLAB: g = x;
    # MATLAB: if n == 1
    # MATLAB: g(1, :, :) = 0;
    # MATLAB: elseif n == 2
    # MATLAB: g(:, 1, :) = 0;
    # MATLAB: elseif n == 3
    # MATLAB: g(:, :, 1) = 0;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: g = (  g - circshift(x, -myShift)  )/dX_u(1, n);
    # MATLAB: g = reshape(g, [prod(n_u(:)), 1]);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    g = None
    return g
