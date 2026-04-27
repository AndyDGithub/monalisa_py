"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmPointReshape import bmPointReshape
from src.sparseMat.m.bmSparseMat_r_nJump2index import bmSparseMat_r_nJump2index
from third_part.matlab_compat.matlab_native import double, repmat
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmImDeformField2sparseMat_ind_weight(v, N_u, Dn, torus_flag):
    # initial -----------------------------------------------------------------
    v           = double(bmPointReshape(v))
    Dn          = double(Dn.ravel().T)
    N_u         = double(N_u.ravel().T)
    imDim       = double(np.shape(v, 1))
    nPt         = double(np.shape(v, 2))
    # TODO(matlab-control): if nPt ~= prod(N_u(:))
    # TODO(matlab-line): error([  'In bmImDeformField_Gn_Gu_Gut : the deformation', ...
    " field must have as many vectors as ",
    # TODO(matlab-line): 'the number of pixel(voxel) in the image. ']);
    # END_initial -------------------------------------------------------------
    # preparing Nu and t and --------------------------------------------------
    Nx_u = 0
    Ny_u = 0
    Nz_u = 0
    # TODO(matlab-control): if imDim == 1
    Nx_u = N_u(1, 1)
    v = np.reshape(v, [1, Nx_u])
    # TODO(matlab-line): x_u = ndgrid(1:Nx_u);
    t = x_u.ravel().T + v
    # TODO(matlab-control): if imDim == 2
    Nx_u = N_u(1, 1)
    Ny_u = N_u(1, 2)
    v = np.reshape(v, [2, Nx_u*Ny_u])
    # TODO(matlab-line): [x_u, y_u] = ndgrid(1:Nx_u, 1:Ny_u);
    # TODO(matlab-line): t = cat(1, x_u(:)', y_u(:)') + v;
    # TODO(matlab-control): if imDim == 3
    Nx_u = N_u(1, 1)
    Ny_u = N_u(1, 2)
    Nz_u = N_u(1, 3)
    v = np.reshape(v, [3, Nx_u*Ny_u*Nz_u])
    # TODO(matlab-line): [x_u, y_u, z_u] = ndgrid(1:Nx_u, 1:Ny_u, 1:Nz_u);
    # TODO(matlab-line): t = cat(1, x_u(:)', y_u(:)', z_u(:)') + v;
    x_u = 0
    y_u = 0
    z_u = 0
    # END_preparing Nu and t and ----------------------------------------------
    # deleting trajectory points that are out of the spat ---------------------
    deleteMask = np.np.zeros((1, nPt), dtype=bool)
    # TODO(matlab-control): if imDim > 0
    # TODO(matlab-line): deleteMask = deleteMask | (t(1, :) < 1) | (t(1, :) > Nx_u);
    # TODO(matlab-control): if imDim > 1
    # TODO(matlab-line): deleteMask = deleteMask | (t(2, :) < 1) | (t(2, :) > Ny_u);
    # TODO(matlab-control): if imDim > 2
    # TODO(matlab-line): deleteMask = deleteMask | (t(3, :) < 1) | (t(3, :) > Nz_u);
    # END_deleting trajectory points that are out of the spat -----------------
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): cx = ndgrid(0:1);
    c = cx.ravel().T
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): [cx, cy] = ndgrid(0:1, 0:1);
    # TODO(matlab-line): c = [cx(:)'; cy(:)'];
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): [cx, cy, cz] = ndgrid(0:1, 0:1, 0:1);
    # TODO(matlab-line): c = [cx(:)'; cy(:)'; cz(:)'];
    c = repmat(c, [1, 1, nPt])
    nNb = double(np.shape(c, 2))
    t_floor = floor(t)
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
    # TODO(matlab-control): if ~isempty(Dn)
    Dn = np.reshape(Dn, [1, nPt])
    Dn =  repmat(Dn, [nNb, 1])
    # TODO(matlab-line): myWeight = exp(-1./(1-d.^2));
    # TODO(matlab-line): myWeight(isinf(myWeight)) = 0;
    # TODO(matlab-line): myWeight = myWeight.*double(abs(d) < 1); % bump-function
    myWeight = np.reshape(myWeight, [nNb, nPt])
    n = t_floor + c
    d = 0
    t_floor = 0
    t_rest = 0
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
    myOne = np.ones(1, nPt)
    # TODO(matlab-control): if not(torus_flag)
    # TODO(matlab-line): n(:, :, deleteMask) = [];
    # TODO(matlab-line): myWeight(:, deleteMask) = [];
    # TODO(matlab-line): myOne(1, deleteMask) = 0;
    # TODO(matlab-control): if ~isempty(Dn)
    # TODO(matlab-line): Dn(:, deleteMask) = [];
    ind_1 = double(n.ravel())
    ind_2 = double(bmSparseMat_r_nJump2index(nNb*myOne).T)
    myWeight = double(myWeight.ravel())
    Dn = double(Dn.ravel())
    return (ind_1, ind_2, myWeight, Dn)
