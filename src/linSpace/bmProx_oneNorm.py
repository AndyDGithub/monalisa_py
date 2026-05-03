# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
#
# function z = bmProx_oneNorm(w, s)
#
# if iscell(w)
#     z = cell(size(w));
#
#     for i = 1:size(z(:), 1)
#         z{i} = bmProx_oneNorm(w{i}, s);
#     end
#
#     return;
# end
#
# argSize = size(w);
#
# w = single(w(:));
# s = single(abs(s));
# N = size(w(:), 1);
# z = [];
#
# if isreal(w)
#     z = zeros(N, 1, 'single');
#     mask_plus   = single(w > s);
#     mask_minus  = single(w < -s);
#     z = mask_plus.*(w - s) + mask_minus.*(w + s);
#
# else
#     w_real = real(w);
#     w_imag = imag(w);
#
#     mask_plus   = single(w_real > s);
#     mask_minus  = single(w_real < -s);
#     z_real      = mask_plus.*(w_real - s) + mask_minus.*(w_real + s);
#     mask_plus   = single(w_imag > s);
#     mask_minus  = single(w_imag < -s);
#     z_imag      = mask_plus.*(w_imag - s) + mask_minus.*(w_imag + s);
#     z = complex(z_real, z_imag);
#
# end
#
# z = reshape(z, argSize);

import numpy as np
from third_part.matlab_compat.matlab_native import single

def bmProx_oneNorm(w, s):
    """Compute the proximal operator of the L1 norm for complex and real ar
arrays."""
    # Preserve original shape
    argSize = np.shape(w)

    # Flatten and cast to single precision
    w = np.array(w, dtype=np.single).ravel()
    s = np.array(np.abs(s), dtype=np.single)

    # Initialize output array
    z = np.zeros_like(w, dtype=np.single)

    if np.iscomplexobj(w):
        w_real = np.real(w)
        w_imag = np.imag(w)

        # Real part
        mask_plus = single(w_real > s)
        mask_minus = single(w_real < -s)
        z_real = mask_plus * (w_real - s) + mask_minus * (w_real + s)

        # Imaginary part
        mask_plus = single(w_imag > s)
        mask_minus = single(w_imag < -s)
        z_imag = mask_plus * (w_imag - s) + mask_minus * (w_imag + s)

        z = np.complex64(z_real + 1j * z_imag)
    else:
        mask_plus = single(w > s)
        mask_minus = single(w < -s)
        z = mask_plus * (w - s) + mask_minus * (w + s)

    return np.reshape(z, argSize)
