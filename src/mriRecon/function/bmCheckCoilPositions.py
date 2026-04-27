"""Auto-generated from MATLAB source. Review manually before production use."""

from src.sparseMat.m.bmSparseMat_vec import error
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmCheckCoilPositions(im_main, im_prescan, n_u):
    im_main     = np.abs(im_main)
    im_prescan  = np.abs(im_prescan)
    n_u = n_u.ravel().T
    imDim = np.shape( n_u.ravel() , 1)
    nCh = np.shape(im_main, imDim + 1)
    X1_mean = np.zeros(1, nCh)
    Y1_mean = np.zeros(1, nCh)
    Z1_mean = np.zeros(1, nCh)
    X2_mean = np.zeros(1, nCh)
    Y2_mean = np.zeros(1, nCh)
    Z2_mean = np.zeros(1, nCh)
    # TODO(matlab-control): if imDim == 1
    error("Case not implemented")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if imDim == 2
    nx = n_u(1, 1)
    ny = n_u(1, 2)
    [X, Y] = ndgrid(nx, ny)
    # TODO(matlab-control): for i = 1:nCh
    # TODO(matlab-line): temp_im = im_main(:, :, i);
    temp_im = temp_im/np.sum(temp_im.ravel())
    # TODO(matlab-line): X_mean(1, i) = sum(  X(:).*temp_im(:)  );
    # TODO(matlab-line): Y_mean(1, i) = sum(  Y(:).*temp_im(:)  );
    # TODO(matlab-line): return;
    # TODO(matlab-control): if imDim == 3
    nx = n_u(1, 1)
    ny = n_u(1, 2)
    nz = n_u(1, 3)
    # TODO(matlab-line): [X, Y, Z] = ndgrid(1:nx, 1:ny, 1:nz);
    X = X - (nx/2 + 1)
    Y = Y - (ny/2 + 1)
    Z = Z - (nz/2 + 1)
    # TODO(matlab-control): for i = 1:nCh
    # TODO(matlab-line): temp_im = im_main(:, :, :, i);
    temp_im = temp_im/np.sum(temp_im.ravel())
    # TODO(matlab-line): X1_mean(1, i) = sum(  X(:).*temp_im(:)  );
    # TODO(matlab-line): Y1_mean(1, i) = sum(  Y(:).*temp_im(:)  );
    # TODO(matlab-line): Z1_mean(1, i) = sum(  Z(:).*temp_im(:)  );
    # TODO(matlab-control): for i = 1:nCh
    # TODO(matlab-line): temp_im = im_prescan(:, :, :, i);
    temp_im = temp_im/np.sum(temp_im.ravel())
    # TODO(matlab-line): X2_mean(1, i) = sum(  X(:).*temp_im(:)  );
    # TODO(matlab-line): Y2_mean(1, i) = sum(  Y(:).*temp_im(:)  );
    # TODO(matlab-line): Z2_mean(1, i) = sum(  Z(:).*temp_im(:)  );
    a = 0.65
    X2_mean = X2_mean*a
    Y2_mean = Y2_mean*a
    Z2_mean = Z2_mean*a
    figure
    # TODO(matlab-line): hold on
    plot3(X1_mean, Y1_mean, Z1_mean, "b.")
    plot3(X2_mean, Y2_mean, Z2_mean, "r.")
    # TODO(matlab-control): for i = 1:nCh
    # TODO(matlab-line): plot3([X1_mean(1, i), X2_mean(1, i)], ...
    [Y1_mean(1, i), Y2_mean(1, i)],
    # TODO(matlab-line): [Z1_mean(1, i), Z2_mean(1, i)], 'k-');
    # TODO(matlab-line): return;
    return (X1_mean, Y1_mean, Z1_mean, X2_mean, Y2_mean, Z2_mean)
