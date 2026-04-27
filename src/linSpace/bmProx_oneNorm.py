import numpy as np
from third_part.matlab_compat.matlab_native import single

def bmProx_oneNorm(w, s):
    argSize = np.shape(w)
    w = single(w.ravel())
    s = single(np.abs(s))
    N = np.shape(w.ravel(), 1)

    z = np.zeros((N,), dtype=np.single)
    mask_plus = single(w > s)
    mask_minus = single(w < -s)

    if w.dtype == np.complex128 or w.dtype == np.complex:
        w_real = np.real(w)
        w_imag = np.imag(w)

        z_real = mask_plus * (w_real - s) + mask_minus * (w_real + s)
        mask_plus = single(w_imag > s)
        mask_minus = single(w_imag < -s)
        z_imag = mask_plus * (w_imag - s) + mask_minus * (w_imag + s)

        z = complex(z_real, z_imag)
    else:  # isreal(w)
        z = mask_plus * (w - s) + mask_minus * (w + s)

    return np.reshape(z, argSize)
