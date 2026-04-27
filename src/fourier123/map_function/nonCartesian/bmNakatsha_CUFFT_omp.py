"""Auto-generated from MATLAB source. Review manually before production use."""

from third_part.matlab_compat.matlab_native import double, single

from src.sparseMat.m.bmSparseMat_vec import error
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmNakatsha_CUFFT_omp(y, G, KFC_conj):
    # argin_initial -----------------------------------------------------------
    N_u     = double(single(G.N_u.ravel().T))
    nPt     = double(G.r_size)
    imDim   = np.shape(N_u.ravel(), 1)
    nCh     = np.shape(y, 2)
    private_check(y, G, KFC_conj, N_u, nCh, nPt)
    # END_argin_initial -------------------------------------------------------
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): [x_real, x_imag] = bmNakatsha1_CUFFT_omp_mex(  real(y), imag(y), real(KFC_conj), imag(KFC_conj), int32(N_u), ...
    G.r_size, G.r_jump, G.r_nJump,
    G.m_val,
    # TODO(matlab-line): G.l_size, G.l_jump, G.l_nJump);
    x = x_real + 1j*x_imag
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): [x_real, x_imag] = bmNakatsha2_CUFFT_omp_mex(  real(y), imag(y), real(KFC_conj), imag(KFC_conj), int32(N_u), ...
    G.r_size, G.r_jump, G.r_nJump,
    G.m_val,
    # TODO(matlab-line): G.l_size, G.l_jump, G.l_nJump);
    x = x_real + 1j*x_imag
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): [x_real, x_imag] = bmNakatsha3_CUFFT_omp_mex(  real(y), imag(y), real(KFC_conj), imag(KFC_conj), int32(N_u), ...
    G.r_size, G.r_jump, G.r_nJump,
    G.m_val,
    # TODO(matlab-line): G.l_size, G.l_jump, G.l_nJump);
    x = x_real + 1j*x_imag
    return x

def k(y, G, KFC_conj, N_u, nCh, nPt):
    # TODO(matlab-control): if not(isa(y, 'single'))
    error("The data""y"" must be of class single")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if not(isa(KFC_conj, 'single'))
    error("The matrix ""KFC_conj"" must be of class single")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if not(isequal(size(y), [nPt, nCh]))
    error("The data matrix ""y"" is not in the correct size")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if not(isequal(size(KFC_conj), [prod(N_u(:)), nCh] ))
    error("The matrix ""KFC_conj"" is not in the correct size")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if sum(mod(N_u(:), 2)) > 0
    error("N_u must have all components even for the Fourier transform. ")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if not(strcmp(G.block_type, 'one_block'))
    error("The block type of G must be ""one_block"". ")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if strcmp(class(G), 'bmSparseMat')
    # TODO(matlab-control): if not(strcmp(G.type, 'cpp_prepared')) && not(strcmp(G.type, 'l_squeezed_cpp_prepared'))
    error("G is bmSparseMat but is not cpp_prepared. ")
    # TODO(matlab-line): return;
    return private_chec
