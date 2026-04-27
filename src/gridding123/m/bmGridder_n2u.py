"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmPointReshape import bmPointReshape
from src.varargin.bmVarargin import bmVarargin
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import bmVarargin_kernelType_nWin_kernelParam
from third_part.matlab_compat.matlab_native import double, repmat, single

from src.sparseMat.m.bmSparseMat_vec import imag, int32, real

from src.image123.bmImGaussFiltering import normpdf
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# I thank
# 
# Gabriele Bonanno
# 
# for the help he brought about gridders at the
# early stage of developpment of the
# reconstruciton code.

import numpy as np

def bmGridder_n2u(data_n, t, Dn, N_u, dK_u, varargin):
    # argin initial -----------------------------------------------------------
    [kernelType, nWin, kernelParam] = bmVarargin(varargin)
    [kernelType, nWin, kernelParam] = bmVarargin_kernelType_nWin_kernelParam(kernelType, nWin, kernelParam)
    t           = double(bmPointReshape(t))
    data_n      = single(bmPointReshape(data_n))
    Dn          = double(bmPointReshape(Dn))
    nCh         = double(np.shape(data_n, 1))
    nPt         = double(np.shape(data_n, 2))
    imDim       = double(np.shape(t, 1))
    N_u         = double(N_u.ravel().T)
    dK_u        = double(dK_u.ravel().T)
    nWin        = double(nWin.ravel().T)
    kernelParam = double(kernelParam.ravel().T)
    # END_argin initial -------------------------------------------------------
    # preparing Nu and t ------------------------------------------------------
    Nx_u = 0
    Ny_u = 0
    Nz_u = 0
    Nu_tot = 1
    # TODO(matlab-control): if imDim > 0
    Nx_u = N_u(1, 1)
    Nu_tot = Nu_tot*Nx_u
    # TODO(matlab-line): t(1, :) = t(1, :)/dK_u(1, 1);
    Dn = Dn/dK_u(1, 1)
    myTrajShift = fix(Nx_u/2 + 1)
    # TODO(matlab-control): if imDim > 1
    Ny_u = N_u(1, 2)
    Nu_tot = Nu_tot*Ny_u
    # TODO(matlab-line): t(2, :) = t(2, :)/dK_u(1, 2);
    Dn = Dn/dK_u(1, 2)
    myTrajShift = [fix(Nx_u/2 + 1), fix(Ny_u/2 + 1)].T
    # TODO(matlab-control): if imDim > 2
    Nz_u = N_u(1, 3)
    Nu_tot = Nu_tot*Nz_u
    # TODO(matlab-line): t(3, :) = t(3, :)/dK_u(1, 3);
    Dn = Dn/dK_u(1, 3)
    myTrajShift = [fix(Nx_u/2 + 1), fix(Ny_u/2 + 1), fix(Nz_u/2 + 1)].T
    t = t + repmat(myTrajShift, [1, nPt])
    # END_preparing Nu and t --------------------------------------------------
    # deleting trajectory points that are out of the spat ---------------------
    temp_mask = np.np.zeros((1, nPt), dtype=bool)
    # TODO(matlab-control): if imDim > 0
    # TODO(matlab-line): temp_mask = temp_mask | (t(1, :) < 1) | (t(1, :) > Nx_u);
    # TODO(matlab-control): if imDim > 1
    # TODO(matlab-line): temp_mask = temp_mask | (t(2, :) < 1) | (t(2, :) > Ny_u);
    # TODO(matlab-control): if imDim > 2
    # TODO(matlab-line): temp_mask = temp_mask | (t(3, :) < 1) | (t(3, :) > Nz_u);
    # TODO(matlab-line): t(:, temp_mask)         = [];
    # TODO(matlab-line): data_n(:, temp_mask)    = [];
    # TODO(matlab-line): Dn(:, temp_mask)        = [];
    nPt = np.shape(t, 2)
    # END_deleting trajectory points that are out of the spat -----------------
    # we make a cas differentiation between even and odd window-width.
    # TODO(matlab-control): if mod(nWin, 2) == 0  % for even window-width
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): cx = ndgrid(-nWin/2-1:nWin/2);
    myFloorShift = 0
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): [cx, cy] = ndgrid(-nWin/2-1:nWin/2, -nWin/2-1:nWin/2);
    myFloorShift = [0, 0].T
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): [cx, cy, cz] = ndgrid(-nWin/2-1:nWin/2, -nWin/2-1:nWin/2, -nWin/2-1:nWin/2);
    myFloorShift = [0, 0, 0].T
    # TODO(matlab-control): else % for odd window-width
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): cx = ndgrid(-fix(nWin/2):fix(nWin/2));
    myFloorShift = 0.5
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): [cx, cy] = ndgrid(-fix(nWin/2):fix(nWin/2), -fix(nWin/2):fix(nWin/2));
    myFloorShift = [0.5, 0.5].T
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): [cx, cy, cz] = ndgrid(-fix(nWin/2):fix(nWin/2), -fix(nWin/2):fix(nWin/2), -fix(nWin/2):fix(nWin/2));
    myFloorShift = [0.5, 0.5, 0.5].T
    # TODO(matlab-control): if imDim == 1
    c = cx.ravel().T
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): c = [cx(:)'; cy(:)'];
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): c = [cx(:)'; cy(:)'; cz(:)'];
    c = repmat(c, [1, 1, nPt])
    nNb = double(np.shape(c, 2))
    t_floor = floor(t + repmat(myFloorShift, [1, nPt]))
    t_rest  = t - t_floor
    t_floor = np.reshape(t_floor, [imDim, 1, nPt])
    t_floor =  repmat(t_floor, [1, nNb, 1])
    t_rest  = np.reshape(t_rest,  [imDim, 1, nPt])
    t_rest  =  repmat(t_rest,  [1, nNb, 1])
    d = t_rest - c
    temp_square = 0
    # TODO(matlab-control): for i = 1:imDim
    # TODO(matlab-line): temp_square = temp_square + d(i, :, :).^2;
    d = sqrt(temp_square)
    Dn = np.reshape(Dn, [1, nPt])
    Dn =  repmat(Dn, [nNb, 1])
    # TODO(matlab-control): if strcmp(kernelType, 'gauss')
    mySigma     = kernelParam(1)
    K_max       = kernelParam(2)
    myWeight    = normpdf(d.ravel(), 0, mySigma)
    # TODO(matlab-control): elseif strcmp(kernelType, 'kaiser')
    myTau       = kernelParam(1)
    myAlpha     = kernelParam(2)
    K_max       = kernelParam(3)
    I0myAlpha   = besseli(0, myAlpha)
    # TODO(matlab-line): myWeight    = max(1-(d/myTau).^2, 0);
    myWeight    = myAlpha*sqrt(myWeight)
    myWeight    = besseli(0, myWeight)/I0myAlpha
    # TODO(matlab-line): myWeight = myWeight(:).*Dn(:);
    myWeight = np.reshape(myWeight, [nNb, nPt])
    n = t_floor + c
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): n(1, :, :) = mod(n(1, :, :)-1, Nx_u)+1;
    # TODO(matlab-line): n = 1 + (n(1, :, :) - 1);
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): n(1, :, :) = mod(n(1, :, :)-1, Nx_u)+1;
    # TODO(matlab-line): n(2, :, :) = mod(n(2, :, :)-1, Ny_u)+1;
    # TODO(matlab-line): n = 1 + (n(1, :, :) - 1) + (n(2, :, :) - 1)*Nx_u;
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): n(1, :, :) = mod(n(1, :, :)-1, Nx_u)+1;
    # TODO(matlab-line): n(2, :, :) = mod(n(2, :, :)-1, Ny_u)+1;
    # TODO(matlab-line): n(3, :, :) = mod(n(3, :, :)-1, Nz_u)+1;
    # TODO(matlab-line): n = 1 + (n(1, :, :) - 1) + (n(2, :, :) - 1)*Nx_u + (n(3, :, :) - 1)*Nx_u*Ny_u;
    n = n.ravel()
    nJump = cat(1, 0, n)
    # TODO(matlab-line): nJump = nJump(2:end) - nJump(1:end-1);
    # TODO(matlab-line): nJump(1) = n(1) - 1;
    n = 0
    d = 0
    t_floor = 0
    t_rest = 0
    # bmGridder3_n2u_mex ------------------------------------------------------
    data_n_real = single(real(data_n))
    data_n_imag = single(imag(data_n))
    myWeight    = single(myWeight)
    nJump    = int32(nJump)
    nCh      = int32(nCh)
    nNb      = int32(nNb)
    nPt      = int32(nPt)
    Nu_tot   = int32(Nu_tot)
    [data_u_real, data_u_imag] = bmGridder_n2u_mex(data_n_real, data_n_imag, myWeight, nJump, nCh, nNb, nPt, Nu_tot)
    # END_bmGridder3_n2u_mex --------------------------------------------------
    # reshaping ---------------------------------------------------------------
    data_u = data_u_real + 1j*data_u_imag
    data_u = np.reshape(data_u, [nCh, N_u])
    # END_reshaping -----------------------------------------------------------
    end  # END_function
    return data_u
