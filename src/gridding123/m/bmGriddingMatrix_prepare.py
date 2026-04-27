"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmPointReshape import bmPointReshape
from src.varargin.bmVarargin import bmVarargin
from third_part.matlab_compat.matlab_native import double, repmat, single

from src.sparseMat.m.bmSparseMat_vec import int32
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# t is the arbitrary_grid. It can be cartesian or non-cartesian.
# 
# The possible values of 'gridding_type' are 'G' or 'G_inv'.
# 
# Remember that the choice of multiplying by the matrix or its transpose
# is done at multiplication time. But the gridding matrix given as input
# argument is the same for the direct matrix multiplication and the
# transpose matrix multiplication.
# 
# varargin{1} is nWin. Default value is 3.
# varargin{2} is kernelParam. Default is [0.61, 10]. We use Gaussian
# gridding kernel.
# 
# The pillar_gridd is implicitely given by N_u and d_u. It is assumed that
# the upper_left_corner of the pillar_gridd is located in
# 
# -d_u.*N_u/2 = [-dx*N_x/2 , -dy*N_y/2 , -dz*N_z/2]
# 
# After rescaling by d_u, we shift then t by N_u/2 + 1 so that
# the pillar_gridd has upper_left_corner in [1, 1, 1]. All along, it is of
# course assumed that all components of N_u are even numbers.
# 
# 

from src.gridding123.m.bmGriddingMatrix import bmGriddingMatrix
import numpy as np

def bmGriddingMatrix_prepare(t, N_u, d_u, nCh, gridding_type, varargin):
    # argin initial -----------------------------------------------------------
    [nWin, kernelParam] = bmVarargin(varargin)
    # TODO(matlab-control): if isempty(nWin)
    nWin = 3
    # TODO(matlab-control): if isempty(kernelParam)
    kernelParam = [0.61, 10]
    t           = double(bmPointReshape(t))
    nCh         = double(nCh)
    nPt         = double(np.shape(t, 2))
    N_u         = double(N_u.ravel().T)
    imDim       = double(np.shape(N_u.ravel(), 1))
    d_u         = double(d_u.ravel().T)
    nWin        = double(nWin)
    # END_argin initial -------------------------------------------------------
    # preparing Nu and t ------------------------------------------------------
    Nx_u = 0
    Ny_u = 0
    Nz_u = 0
    # TODO(matlab-control): if imDim > 0
    Nx_u = N_u(1, 1)
    # TODO(matlab-line): t(1, :) = t(1, :)/d_u(1, 1);
    myTrajShift = fix(Nx_u/2 + 1)
    # TODO(matlab-control): if imDim > 1
    Ny_u = N_u(1, 2)
    # TODO(matlab-line): t(2, :) = t(2, :)/d_u(1, 2);
    myTrajShift = [fix(Nx_u/2 + 1), fix(Ny_u/2 + 1)].T
    # TODO(matlab-control): if imDim > 2
    Nz_u = N_u(1, 3)
    # TODO(matlab-line): t(3, :) = t(3, :)/d_u(1, 3);
    myTrajShift = [fix(Nx_u/2 + 1), fix(Ny_u/2 + 1), fix(Nz_u/2 + 1)].T
    t = t + repmat(myTrajShift, [1, nPt])
    # END_preparing Nu and t --------------------------------------------------
    # deleting trajectory points that are out of the box ----------------------
    temp_mask = np.np.zeros((1, nPt), dtype=bool)
    # TODO(matlab-control): if imDim > 0
    # TODO(matlab-line): temp_mask = temp_mask | (t(1, :) < 1) | (t(1, :) > Nx_u);
    # TODO(matlab-control): if imDim > 1
    # TODO(matlab-line): temp_mask = temp_mask | (t(2, :) < 1) | (t(2, :) > Ny_u);
    # TODO(matlab-control): if imDim > 2
    # TODO(matlab-line): temp_mask = temp_mask | (t(3, :) < 1) | (t(3, :) > Nz_u);
    # TODO(matlab-line): t(:, temp_mask)         = [];
    nPt = np.shape(t, 2)
    # END_deleting trajectory points that are out of the box ------------------
    tx              = []
    ty              = []
    tz              = []
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): tx          = single(t(1, :));
    Nx          = int32(N_u(1, 1))
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): tx          = single(t(1, :));
    # TODO(matlab-line): ty          = single(t(2, :));
    Nx          = int32(N_u(1, 1))
    Ny          = int32(N_u(1, 2))
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): tx          = single(t(1, :));
    # TODO(matlab-line): ty          = single(t(2, :));
    # TODO(matlab-line): tz          = single(t(3, :));
    Nx          = int32(N_u(1, 1))
    Ny          = int32(N_u(1, 2))
    Nz          = int32(N_u(1, 3))
    nCh             = int32(nCh)
    nPt             = int32(nPt)
    nWin            = int32(nWin)
    kernelParam_1   = single(kernelParam(1, 1))
    kernelParam_2   = single(kernelParam(1, 2))
    # TODO(matlab-control): if imDim == 1
    secret_length   = bmGriddingMatrix_secret_length1_mex(tx, nCh, nPt, Nx, nWin)
    # TODO(matlab-control): if strcmp(gridding_type, 'G')
    # TODO(matlab-line): [w, u_ind]      = bmGriddingMatrix_prepare_G1_mex(      tx, Dn, ...
    nCh, nPt, Nx,
    nWin, kernelParam_1, kernelParam_2,
    # TODO(matlab-line): secret_length);
    # TODO(matlab-control): elseif strcmp(gridding_type, 'G_inv')
    # TODO(matlab-line): [w, u_ind]      = bmGriddingMatrix_prepare_G_inv1_mex(  tx, Dn, ...
    nCh, nPt, Nx,
    nWin, kernelParam_1, kernelParam_2,
    # TODO(matlab-line): secret_length);
    # TODO(matlab-control): elseif imDim == 2
    secret_length   = bmGriddingMatrix_secret_length2_mex(tx, ty, tz, nPt, Nx, Ny, nWin)
    # TODO(matlab-control): if strcmp(gridding_type, 'G')
    # TODO(matlab-line): [w, u_ind]      = bmGriddingMatrix_prepare_G2_mex(      tx, ty, Dn, ...
    nCh, nPt, Nx, Ny,
    nWin, kernelParam_1, kernelParam_2,
    # TODO(matlab-line): secret_length);
    # TODO(matlab-control): elseif strcmp(gridding_type, 'G_inv')
    # TODO(matlab-line): [w, u_ind]      = bmGriddingMatrix_prepare_G_inv2_mex(  tx, ty, Dn, ...
    nCh, nPt, Nx, Ny,
    nWin, kernelParam_1, kernelParam_2,
    # TODO(matlab-line): secret_length);
    # TODO(matlab-control): elseif imDim == 3
    secret_length   = bmGriddingMatrix_secret_length3_mex(tx, ty, tz, nCh, nPt, Nx, Ny, Nz, nWin)
    # TODO(matlab-control): if strcmp(gridding_type, 'G')
    # TODO(matlab-line): [w, u_ind]      = bmGriddingMatrix_prepare_G3_mex(      tx, ty, tz, Dn, ...
    nCh, nPt, Nx, Ny, Nz,
    nWin, kernelParam_1, kernelParam_2,
    # TODO(matlab-line): secret_length);
    # TODO(matlab-control): elseif strcmp(gridding_type, 'G_inv')
    # TODO(matlab-line): [w, u_ind]      = bmGriddingMatrix_prepare_G_inv3_mex(  tx, ty, tz, Dn, ...
    nCh, nPt, Nx, Ny, Nz,
    nWin, kernelParam_1, kernelParam_2,
    # TODO(matlab-line): secret_length);
    # TODO(matlab-line): griddingMatrix = bmGriddingMatrix(  w, u_ind, ...
    nCh, nPt, Nx, Ny, Nz, secret_length,
    # TODO(matlab-line): gridding_type);
    end  # END_function
    return griddingMatrix
