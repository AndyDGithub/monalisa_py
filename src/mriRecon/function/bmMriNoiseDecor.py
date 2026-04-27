"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmZero import bmZero
from third_part.matlab_compat.matlab_native import disp

from src.sparseMat.m.bmSparseMat_vec import error
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# noise_meas is the noise measurment performed during prescan. It must be
# in the size [nPt_noise, nCh] i.e. channel dimension as second dimension.
# 
# y is the complex-valued raw_data and must be in the size [nPt, nCh];
# 
# C is the comlex-valued coil_sense. Lowres preferably in order to
# accelerate the calculation.
# 
# C_n_u is the image size of the (lowres) coil_sense. For example if
# size(C) = [64, 96, 128, 24] (i.e. 24 channels), then is
# C_n_u = [64, 96, 128] because the image size is [64, 96, 128] in that
# case.

import numpy as np

def bmMriNoiseDecor(noise_meas, y, C, C_n_u):
    # initial -----------------------------------------------------------------
    nCh         = np.shape(noise_meas, 2)
    nPt_noise   = np.shape(noise_meas, 1)
    C = bmColReshape(C, C_n_u)
    C_size = np.shape(C)
    C_size = C_size.ravel().T
    C_decor = bmZero(np.shape(C), "complex_single")
    # TODO(matlab-control): if iscell(y)
    nCell   = np.shape(y.ravel())
    y_decor = cell(np.shape(y))
    # TODO(matlab-control): for i = 1:nCell
    y_decor[i] = bmZero(np.shape(y[i]), "complex_single")
    # TODO(matlab-control): else
    y_decor = bmZero(np.shape(y), "complex_single")
    # checking_argins
    # TODO(matlab-control): if ~isequal(nCh, C_size(1, end))
    error("There is a problem with the size of noise_meas and/or with the size of C")
    # TODO(matlab-line): return;
    nPt_noise = np.shape(noise_meas, 1)
    # TODO(matlab-control): if nPt_noise <= nCh
    error("There is a problem with the size of noise_mease. ")
    # TODO(matlab-line): return;
    # END_checking_argins
    disp("Starting noise_decorrelation  ")
    # END_initial -------------------------------------------------------------
    # noise_correlation_matrix_and_cholesky_decomposition ---------------------
    # TODO(matlab-line): psi = (1/(nPt_noise-1))*noise_meas'*noise_meas; % noise_correlation_matrix
    # TODO(matlab-control): for i = 1:nCh
    # cleaning imaginary part coming from trucation errors
    # TODO(matlab-line): psi(i, i) = real(psi(i, i));
    # Cholesky decomposition of psi
    L = chol(psi, "lower")
    # taking inverse
    L_inv = inv(L)
    # normalizing by SOS of diagonal elements in order to approx conserve magnitude
    # TODO(matlab-line): L_inv = L_inv/sqrt(mean(abs(  diag(L_inv)  ).^2));
    # END_noise_correlation_matrix_and_cholesky_decomposition -----------------
    # noise_decorrelation -----------------------------------------------------
    # TODO(matlab-control): if iscell(y)
    nCell   = np.shape(y.ravel())
    # TODO(matlab-control): for i = 1:nCell
    # TODO(matlab-control): for k = 1:nCh
    # TODO(matlab-control): for m = 1:nCh
    # TODO(matlab-line): y_decor{i}(:, k) = y_decor{i}(:, k) + L_inv(k, m)*y{i}(:, m);
    # TODO(matlab-control): else
    # TODO(matlab-control): for k = 1:nCh
    # TODO(matlab-control): for m = 1:nCh
    # TODO(matlab-line): y_decor(:, k) = y_decor(:, k) + L_inv(k, m)*y(:, m);
    # TODO(matlab-control): for k = 1:nCh
    # TODO(matlab-control): for m = 1:nCh
    # TODO(matlab-line): C_decor(:, k) = C_decor(:, k) + L_inv(k, m)*C(:, m);
    # END_noise_decorrelation -----------------------------------------------------
    # final -------------------------------------------------------------------
    C_decor = bmBlockReshape(C_decor, C_n_u)
    disp(" noise_decorrelation done. ")
    # END_final ---------------------------------------------------------------
    return (y_decor, C_decor)
