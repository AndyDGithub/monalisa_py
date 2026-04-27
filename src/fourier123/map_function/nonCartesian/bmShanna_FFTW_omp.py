"""Auto-generated from MATLAB source. Review manually before production use."""

from third_part.matlab_compat.matlab_native import double, single

from src.sparseMat.m.bmSparseMat_vec import error
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmShanna_FFTW_omp(x, G, KFC):
    # argin_initial -----------------------------------------------------------
    N_u         = double(single(G.N_u.ravel().T))
    imDim       = np.shape(N_u.ravel(), 1)
    nCh         = np.shape(KFC, 2)
    private_check(x, G, KFC, N_u, nCh)
    # END_argin_initial -------------------------------------------------------
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): [y_real, y_imag] = bmShanna1_FFTW_omp_mex( real(x), imag(x), real(KFC), imag(KFC), int32(N_u), ...
    G.r_size, G.r_jump, G.r_nJump,
    G.m_val,
    # TODO(matlab-line): G.l_size, G.l_jump, G.l_nJump);
    y = y_real + 1j*y_imag
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): [y_real, y_imag] = bmShanna2_FFTW_omp_mex( real(x), imag(x), real(KFC), imag(KFC), int32(N_u), ...
    G.r_size, G.r_jump, G.r_nJump,
    G.m_val,
    # TODO(matlab-line): G.l_size, G.l_jump, G.l_nJump);
    y = y_real + 1j*y_imag
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): [y_real, y_imag] = bmShanna3_FFTW_omp_mex( real(x), imag(x), real(KFC), imag(KFC), int32(N_u), ...
    G.r_size, G.r_jump, G.r_nJump,
    G.m_val,
    # TODO(matlab-line): G.l_size, G.l_jump, G.l_nJump);
    y = y_real + 1j*y_imag
    return y

def k(x, G, KFC, N_u, nCh):
    # TODO(matlab-control): if not(isa(x, 'single'))
    error("The data""x"" must be of class single")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if not(isa(KFC, 'single'))
    error("The matrix ""KFC"" must be of class single")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if not(size(x, 1) == prod(N_u(:)))
    error("The data matrix ""x"" is not in the correct size")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if not(isequal(size(KFC), [prod(N_u(:)), nCh] ))
    error("The matrix ""K"" is probably not in the correct size")
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
