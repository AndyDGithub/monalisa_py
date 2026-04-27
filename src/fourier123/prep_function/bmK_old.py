"""Auto-generated from MATLAB source. Review manually before production use."""

from src.varargin.bmVarargin import bmVarargin
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import bmVarargin_kernelType_nWin_kernelParam
from third_part.matlab_compat.matlab_native import double, repmat, single

from src.sparseMat.m.bmSparseMat_vec import error, real

from src.image123.bmImGaussFiltering import normpdf
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmK_old(N_u, dK_u, nCh, varargin):
    # argin_initial -----------------------------------------------------------
    [kernelType, nWin, kernelParam] = bmVarargin(varargin)
    [kernelType, nWin, kernelParam] = bmVarargin_kernelType_nWin_kernelParam(kernelType, nWin, kernelParam)
    N_u         = double(single(N_u.ravel().T))
    dK_u        = double(single(dK_u.ravel().T))
    nWin        = double(single(nWin.ravel().T))
    kernelParam = double(single(kernelParam.ravel().T))
    K           = np.zeros(1, prod(N_u.ravel()), "double")
    imDim       = double(np.shape(N_u.ravel(), 1))
    nCh         = double(single(nCh))
    # TODO(matlab-control): if sum(mod(N_u(:), 2)) > 0
    error("N_u must have all components even for the Fourier transform. ")
    # TODO(matlab-line): return;
    # END_argin_initial -------------------------------------------------------
    myTrajPoint = (fix(N_u/2) + 1).T
    # TODO(matlab-line): myWin       = -fix(nWin/2):fix(nWin/2);
    # TODO(matlab-control): if imDim == 1
    cx = ndgrid(myWin)
    c = cx.ravel().T
    n = c + repmat(myTrajPoint ,[1, np.shape(c, 2)])
    # TODO(matlab-line): nMask = (n(1, :) < 1) | (n(1, :) > N_u(1, 1));
    # TODO(matlab-control): elseif imDim == 2
    [cx, cy] = ndgrid(myWin, myWin)
    # TODO(matlab-line): c = [cx(:)'; cy(:)'];
    n = c + repmat(myTrajPoint ,[1, np.shape(c, 2)])
    # TODO(matlab-line): nMask = (n(1, :) < 1) | (n(2, :) < 1) | (n(1, :) > N_u(1, 1)) | (n(2, :) > N_u(1, 2));
    # TODO(matlab-control): elseif imDim == 3
    [cx, cy, cz] = ndgrid(myWin, myWin, myWin)
    # TODO(matlab-line): c = [cx(:)'; cy(:)'; cz(:)'];
    n = c + repmat(myTrajPoint ,[1, np.shape(c, 2)])
    # TODO(matlab-line): nMask = (n(1, :) < 1) | (n(2, :) < 1) | (n(3, :) < 1) | (n(1, :) > N_u(1, 1)) | (n(2, :) > N_u(1, 2)) | (n(3, :) > N_u(1, 3));
    # TODO(matlab-line): n = n(:, not(nMask));
    myDiff = repmat(myTrajPoint, [1, np.shape(n, 2)]) - n
    d = np.zeros(1, np.shape(myDiff, 2))
    # TODO(matlab-control): for i = 1:imDim
    # TODO(matlab-line): d = d + myDiff(i, :).^2;
    d = sqrt(d)
    # TODO(matlab-control): if strcmp(kernelType, 'gauss')
    myWeight = normpdf(d.ravel(), 0, kernelParam)
    # TODO(matlab-control): elseif strcmp(kernelType, 'kaiser')
    tau     = kernelParam(1)
    alpha   = kernelParam(2)
    I0alpha = besseli(0, alpha)
    # TODO(matlab-line): myWeight = max(1-(d/tau).^2, 0);
    myWeight = alpha*sqrt(myWeight)
    myWeight = besseli(0, myWeight)/I0alpha
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): myIndexList = 1 + (n(1, :) - 1);
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): myIndexList = 1 + (n(1, :) - 1) + (n(2, :) - 1)*N_u(1, 1);
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): myIndexList = 1 + (n(1, :) - 1) + (n(2, :) - 1)*N_u(1, 1) + (n(3, :) - 1)*N_u(1, 1)*N_u(1, 2);
    # TODO(matlab-line): K(1, myIndexList) = myWeight;
    K = np.reshape(K, [N_u, 1])
    # TODO(matlab-control): if imDim > 0
    K = fftshift(np.fft.ifft(ifftshift(K, 1), [], 1), 1)*N_u(1, 1)*dK_u(1, 1)
    # TODO(matlab-control): if imDim > 1
    K = fftshift(np.fft.ifft(ifftshift(K, 2), [], 2), 2)*N_u(1, 2)*dK_u(1, 2)
    # TODO(matlab-control): if imDim > 2
    K = fftshift(np.fft.ifft(ifftshift(K, 3), [], 3), 3)*N_u(1, 3)*dK_u(1, 3)
    K = real(K)
    K = (K/max(K.ravel()))
    K = single(1./K)
    K = repmat(K.ravel(), [1, nCh])
    K = single(K)
    return K
