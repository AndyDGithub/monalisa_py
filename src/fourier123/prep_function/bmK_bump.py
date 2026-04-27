"""Auto-generated from MATLAB source. Review manually before production use."""

from src.fourier1.bmDFT1 import bmDFT1
from src.fourier2.bmDFT2 import bmDFT2
from src.fourier3.bmDFT3 import bmDFT3
from third_part.matlab_compat.matlab_native import double, single

from src.sparseMat.m.bmSparseMat_vec import error, int32, real
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmK_bump(N_u):
    # argin initial -----------------------------------------------------------
    arg_osf = 2;  # --------------------------------------------------------------- magic_number
    N_u         = double(int32(N_u.ravel().T))
    N_u_os      = round(N_u*arg_osf)
    imDim       = np.shape(N_u.ravel(), 1)
    # TODO(matlab-control): if sum(mod(N_u(:), 2)) > 0
    error("N_u must have all components even for the Fourier transform. ")
    # TODO(matlab-line): return;
    # END_argin initial -------------------------------------------------------
    Nx_u = 0
    Ny_u = 0
    Nz_u = 0
    # TODO(matlab-control): if imDim == 1
    Nx_u = N_u(1, 1)
    # TODO(matlab-control): if imDim == 2
    Nx_u = N_u(1, 1)
    Ny_u = N_u(1, 2)
    # TODO(matlab-control): if imDim == 3
    Nx_u = N_u(1, 1)
    Ny_u = N_u(1, 2)
    Nz_u = N_u(1, 3)
    x = []
    y = []
    z = []
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): x = (-Nx_u*arg_osf/2:Nx_u*arg_osf/2-1)/arg_osf;
    x = ndgrid(x)
    # TODO(matlab-line): d = sqrt(x(:).^2);
    d = np.reshape(d, [N_u_os, 1])
    # TODO(matlab-control): if imDim == 2
    # TODO(matlab-line): x = (-Nx_u*arg_osf/2:Nx_u*arg_osf/2-1)/arg_osf;
    # TODO(matlab-line): y = (-Ny_u*arg_osf/2:Ny_u*arg_osf/2-1)/arg_osf;
    [x, y] = ndgrid(x, y)
    # TODO(matlab-line): d = sqrt(x(:).^2 + y(:).^2);
    d = np.reshape(d, N_u_os)
    # TODO(matlab-control): if imDim == 3
    # TODO(matlab-line): x = (-Nx_u*arg_osf/2:Nx_u*arg_osf/2-1)/arg_osf;
    # TODO(matlab-line): y = (-Ny_u*arg_osf/2:Ny_u*arg_osf/2-1)/arg_osf;
    # TODO(matlab-line): z = (-Nz_u*arg_osf/2:Nz_u*arg_osf/2-1)/arg_osf;
    [x, y, z] = ndgrid(x, y, z)
    # TODO(matlab-line): d = sqrt(x(:).^2 + y(:).^2 + z(:).^2);
    d = np.reshape(d, N_u_os)
    # TODO(matlab-line): myWeight = exp(-1./(1-d.^2));
    # TODO(matlab-line): myWeight(isinf(myWeight)) = 0;
    # TODO(matlab-line): myWeight = myWeight.*double(abs(d) < 1); % bump-function
    # TODO(matlab-control): if imDim == 1
    K = bmDFT1(myWeight, N_u_os, 1./N_u)
    # TODO(matlab-control): elseif imDim == 2
    K = bmDFT2(myWeight, N_u_os, 1./N_u)
    # TODO(matlab-control): elseif imDim == 3
    K = bmDFT3(myWeight, N_u_os, 1./N_u)
    # TODO(matlab-control): if imDim == 1
    x_center    = N_u_os(1, 1)/2+1
    x_half      = N_u(1, 1)/2
    # TODO(matlab-line): x_ind       = x_center-x_half:x_center+x_half-1;
    K = K.ravel()
    K = K(x_ind, 1)
    # TODO(matlab-control): elseif imDim == 2
    x_center    = N_u_os(1, 1)/2+1
    x_half      = N_u(1, 1)/2
    # TODO(matlab-line): x_ind       = x_center-x_half:x_center+x_half-1;
    y_center    = N_u_os(1, 2)/2+1
    y_half      = N_u(1, 2)/2
    # TODO(matlab-line): y_ind       = y_center-y_half:y_center+y_half-1;
    K = K(x_ind, y_ind)
    # TODO(matlab-control): elseif imDim == 3
    x_center    = N_u_os(1, 1)/2+1
    x_half      = N_u(1, 1)/2
    # TODO(matlab-line): x_ind       = x_center-x_half:x_center+x_half-1;
    y_center    = N_u_os(1, 2)/2+1
    y_half      = N_u(1, 2)/2
    # TODO(matlab-line): y_ind       = y_center-y_half:y_center+y_half-1;
    z_center    = N_u_os(1, 3)/2+1
    z_half      = N_u(1, 3)/2
    # TODO(matlab-line): z_ind       = z_center-z_half:z_center+z_half-1;
    K = K(x_ind, y_ind, z_ind)
    K = real(K)
    K = K/max(np.abs(K.ravel()))
    K = single(1./K)
    end  # END_function
    return K
