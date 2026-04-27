"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmColReshape import bmColReshape
from src.varargin.bmVarargin import bmVarargin
from third_part.matlab_compat.matlab_native import double, single

from src.sparseMat.m.bmSparseMat_vec import error
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmShanna_cartesian(x, N_u, dK_u, varargin):
    # argin_initial -----------------------------------------------------------
    x       = bmColReshape(x, N_u)
    N_u     = double(N_u.ravel().T)
    imDim   = np.shape(N_u.ravel(), 1)
    nCh     = np.shape(x, 2)
    F       = single(1/prod(  single(N_u.ravel())  )/prod(  single(dK_u.ravel())  ))
    C = bmVarargin(varargin)
    C_flag = False
    # TODO(matlab-control): if not(isempty(C))
    C_flag = True
    nCh = np.shape(C, 2)
    C = single(C)
    private_check(x, N_u)
    # END_argin_initial -------------------------------------------------------
    # coil decombine
    # TODO(matlab-control): if C_flag
    # TODO(matlab-line): x = C.*repmat(x, [1, nCh]);
    # fft
    y = np.reshape(x, [N_u, nCh])
    # TODO(matlab-control): for n = 1:3
    # TODO(matlab-control): if imDim > (n-1)
    y = fftshift(np.fft.fft(ifftshift(y, n), [], n), n)
    y = np.reshape(y, [prod(N_u.ravel()), nCh])
    y = y*F
    return y

def k(x, N_u):
    # TODO(matlab-control): if not(strcmp(class(x), 'single'))
    error("The data""x"" must be of class single")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if size(x, 2) > size(x, 1)
    error("The data matrix ""x"" is probably not in the correct size")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if sum(mod(N_u(:), 2)) > 0
    error("N_u must have all components even for the Fourier transform. ")
    # TODO(matlab-line): return;
    return private_chec
