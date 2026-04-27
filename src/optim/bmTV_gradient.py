from __future__ import annotations
from third_part.matlab_compat.matlab_native import size
from porting.lib.utils import imag, real


def bmTV_gradient(x, N_u, dX_u):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: imDim   = size(N_u(:), 1);
    # MATLAB: N_u     = N_u(:)';
    # MATLAB: dX_u    = dX_u(:)';
    # MATLAB: D_u     = prod(dX_u(:));
    # MATLAB: if imDim == 1
    # MATLAB: g = zeros([N_u, 1], 'single');
    # MATLAB: g = complex(g, g);
    # MATLAB: x_real = reshape(real(x), [N_u, 1]);
    # MATLAB: x_imag = reshape(imag(x), [N_u, 1]);
    # MATLAB: myShift_1 = [1, 0];
    # MATLAB: g_real = circshift(x_real, myShift_1);
    # MATLAB: g_imag = circshift(x_imag, myShift_1);
    # MATLAB: g_real = sign(x_real - g_real)/dX_u(1, 1);
    # MATLAB: g_imag = sign(x_imag - g_imag)/dX_u(1, 1);
    # MATLAB: g_real(1, 1) = 0;
    # MATLAB: g_imag(1, 1) = 0;
    # MATLAB: g_real = g_real - circshift(g_real, - myShift_1);
    # MATLAB: g_imag = g_imag - circshift(g_imag, - myShift_1);
    # MATLAB: g = g + complex(g_real, g_imag);
    # MATLAB: elseif imDim == 2
    # MATLAB: g = zeros(N_u, 'single');
    # MATLAB: g = complex(g, g);
    # MATLAB: x_real = reshape(real(x), N_u);
    # MATLAB: x_imag = reshape(imag(x), N_u);
    # MATLAB: myShift_1 = [1, 0];
    # MATLAB: myShift_2 = [0, 1];
    # MATLAB: g_real = circshift(x_real, myShift_1);
    # MATLAB: g_imag = circshift(x_imag, myShift_1);
    # MATLAB: g_real = sign(x_real - g_real)/dX_u(1, 1);
    # MATLAB: g_imag = sign(x_imag - g_imag)/dX_u(1, 1);
    # MATLAB: g_real(1, :) = 0;
    # MATLAB: g_imag(1, :) = 0;
    # MATLAB: g_real = g_real - circshift(g_real, - myShift_1);
    # MATLAB: g_imag = g_imag - circshift(g_imag, - myShift_1);
    # MATLAB: g = g + complex(g_real, g_imag);
    # MATLAB: g_real = circshift(x_real, myShift_2);
    # MATLAB: g_imag = circshift(x_imag, myShift_2);
    # MATLAB: g_real = sign(x_real - g_real)/dX_u(1, 2);
    # MATLAB: g_imag = sign(x_imag - g_imag)/dX_u(1, 2);
    # MATLAB: g_real(:, 1) = 0;
    # MATLAB: g_imag(:, 1) = 0;
    # MATLAB: g_real = g_real - circshift(g_real, - myShift_2);
    # MATLAB: g_imag = g_imag - circshift(g_imag, - myShift_2);
    # MATLAB: g = g + complex(g_real, g_imag);
    # MATLAB: elseif imDim == 3
    # MATLAB: g = zeros(N_u, 'single');
    # MATLAB: g = complex(g, g);
    # MATLAB: x_real = reshape(real(x), N_u);
    # MATLAB: x_imag = reshape(imag(x), N_u);
    # MATLAB: myShift_1 = [1, 0, 0];
    # MATLAB: myShift_2 = [0, 1, 0];
    # MATLAB: myShift_3 = [0, 0, 1];
    # MATLAB: g_real = circshift(x_real, myShift_1);
    # MATLAB: g_imag = circshift(x_imag, myShift_1);
    # MATLAB: g_real = sign(x_real - g_real)/dX_u(1, 1);
    # MATLAB: g_imag = sign(x_imag - g_imag)/dX_u(1, 1);
    # MATLAB: g_real(1, :, :) = 0;
    # MATLAB: g_imag(1, :, :) = 0;
    # MATLAB: g_real = g_real - circshift(g_real, - myShift_1);
    # MATLAB: g_imag = g_imag - circshift(g_imag, - myShift_1);
    # MATLAB: g = g + complex(g_real, g_imag);
    # MATLAB: g_real = circshift(x_real, myShift_2);
    # MATLAB: g_imag = circshift(x_imag, myShift_2);
    # MATLAB: g_real = sign(x_real - g_real)/dX_u(1, 2);
    # MATLAB: g_imag = sign(x_imag - g_imag)/dX_u(1, 2);
    # MATLAB: g_real(:, 1, :) = 0;
    # MATLAB: g_imag(:, 1, :) = 0;
    # MATLAB: g_real = g_real - circshift(g_real, - myShift_2);
    # MATLAB: g_imag = g_imag - circshift(g_imag, - myShift_2);
    # MATLAB: g = g + complex(g_real, g_imag);
    # MATLAB: g_real = circshift(x_real, myShift_3);
    # MATLAB: g_imag = circshift(x_imag, myShift_3);
    # MATLAB: g_real = sign(x_real - g_real)/dX_u(1, 3);
    # MATLAB: g_imag = sign(x_imag - g_imag)/dX_u(1, 3);
    # MATLAB: g_real(:, :, 1) = 0;
    # MATLAB: g_imag(:, :, 1) = 0;
    # MATLAB: g_real = g_real - circshift(g_real, - myShift_3);
    # MATLAB: g_imag = g_imag - circshift(g_imag, - myShift_3);
    # MATLAB: g = g + complex(g_real, g_imag);
    # MATLAB: end
    # MATLAB: g = g*D_u;
    # MATLAB: g = reshape(g, [prod(N_u(:)), 1]);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    g = None
    return g
