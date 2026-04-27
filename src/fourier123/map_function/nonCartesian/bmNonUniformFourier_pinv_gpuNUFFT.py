"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.coilSense.map.bmCoilSense_pinv import bmCoilSense_pinv
from src.fourier123.other_function.bmOverSamplingFactor_for_gpuNUFFT import bmOverSamplingFactor_for_gpuNUFFT
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from src.mask123.bmElipsoidMask import bmElipsoidMask
from src.mriRecon.function.bmSimulateMriData import bmSimulateMriData
from src.traj123.bmTraj_rescaleToUnitCube import bmTraj_rescaleToUnitCube
from third_part.matlab_compat.matlab_native import double, single

from src.sparseMat.m.bmSparseMat_vec import error, int32
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# 
# 
# 
# y is the data.
# 
# t is the trajectory;
# 
# ve is the volumeElement;
# 
# C is the coil sensitivity.
# 
# N_u is the size of the fourier grid.
# 
# n_u is the size of the image (can be empty).
# 
# dK_u is the edge-size of a cell of the fourier grid.

import numpy as np

def bmNonUniformFourier_pinv_gpuNUFFT(y, t, ve, C, N_u, n_u, dK_u, ve_max):
    # initial -----------------------------------------------------------------
    # TODO(matlab-control): if isempty(n_u)
    n_u = N_u
    # TODO(matlab-control): if sum(mod(N_u(:), 2)) > 0
    error("N_u must have all components even for the Fourier transform. ")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if sum(mod(n_u(:), 2)) > 0
    error("n_u must have all components even for the Fourier transform. ")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if size(y, 2) >= size(y, 1)
    # TODO(matlab-line): y = y.';
    t       = double(bmPointReshape(t))
    y       = single(bmPointReshape(y))
    ve_col  = single(min(ve.ravel(), ve_max))
    ve      = single(  bmY_ve_reshape(ve_col, np.shape(y))  )
    C       = single(C)
    nPt = np.shape(t, 2)
    N_u         = double(int32(N_u.ravel().T ))
    n_u         = double(int32(n_u.ravel().T ))
    dK_u        = double(single(dK_u.ravel().T))
    # gpuNUFFT_initial
    t_gpuNUFFT      = bmTraj_rescaleToUnitCube(t, N_u, dK_u)
    ve_gpuNUFFT     = np.ones(nPt, 1)
    osf = bmOverSamplingFactor_for_gpuNUFFT(N_u, n_u)
    kw = 3;  # 3 or 1 also possible (nearest neighbor) ------------------------------------------------------- magic_number
    sw = 6;  # N_u should be a multiple of an sw related number --------------------------------------------- magic_number
    atomic = True;  # for rapidity AND for F' (backward NUFFT) to be correct !!!
    textures = True;  # for rapidity
    loadbalancing = True;  # for rapidity
    F_gpuNUFFT = gpuNUFFT(t_gpuNUFFT, ve_gpuNUFFT.ravel(), osf, kw, sw, n_u, [], atomic, textures, loadbalancing)
    factor_gpuNUFFT         = 1/sqrt(prod(N_u.ravel()))/prod(dK_u.ravel())
    # END_gpuNUFFT_initial
    # calibration for rescaling
    h_calib         = single(  bmElipsoidMask(n_u, n_u/4)  );  # -------------------- magic number
    # TODO(matlab-control): if isempty(C)
    ve_calib = ve_col
    # TODO(matlab-control): else
    ve_calib = ve
    y_calib         = bmSimulateMriData(h_calib, C, t, N_u, n_u, dK_u)
    # TODO(matlab-line): x_calib         = factor_gpuNUFFT*(  F_gpuNUFFT'*(y_calib.*ve_calib)  );
    # TODO(matlab-control): if not(isempty(C))
    C = bmBlockReshape(C, n_u)
    x_calib = bmCoilSense_pinv(C, x_calib, n_u)
    x_calib = np.abs(x_calib)
    mask_calib      = bmElipsoidMask(n_u, n_u/4)  ;  # ------------------------- magic_number
    val_calib       = x_calib(mask_calib)
    factor_rescale  = 1/np.mean(  val_calib.ravel()  )
    # END_calibration for rescaling
    # END_initial -------------------------------------------------------------
    # NUFFT
    # TODO(matlab-line): x = factor_rescale*factor_gpuNUFFT*(  F_gpuNUFFT'*(y.*ve)  );
    # eventual coil_combine
    # TODO(matlab-control): if not(isempty(C))
    C = bmBlockReshape(C, n_u)
    x = bmCoilSense_pinv(C, x, n_u)
    end  # END_function
    return x
