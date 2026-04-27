"""Auto-generated from MATLAB source. Review manually before production use."""

from src.imReg.m.bmImReg_deformField_to_positionField import bmImReg_deformField_to_positionField
from src.image123.bmImCrope import bmImCrope
from src.image123.bmImExtend import bmImExtend
from src.image123.bmImGradient import bmImGradient
from third_part.matlab_compat.matlab_native import repmat
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# 
# 'v'               is the deformField.
# 'n_u'             is the image size.
# 'cell_width'      is the width of a cell of the checkerBoared. It must be
# equal or larger to 2.
# 
# 
# We work in image convention i.e. isotropic voxel_size with width equql 1
# in each dimension.
# 
# varargin{1} is an grey_scale image to display as background.
# 
# This function displays the inverse deformField by mean of a
# checherBoared.

import numpy as np

def bmImDeformFieldInverse_gridDisp2(v, n_u, cell_width, varargin):
    nan_value = -1;  # -------------------------------------------------------- magic_number
    backGroundIm = bmVarargin(varargin)
    # TODO(matlab-control): if cell_width < 2
    cell_width = 2
    # TODO(matlab-control): elseif cell_width > min(n_u)
    cell_width = min(n_u)
    v = bmBlockReshape(v, n_u)
    v = bmImReg_deformField_to_positionField(v, n_u, [], [], [], True)
    # TODO(matlab-line): vx = v(:, :, 1);
    # TODO(matlab-line): vy = v(:, :, 2);
    # TODO(matlab-line): X = 1:n_u(1, 1);
    # TODO(matlab-line): Y = 1:n_u(1, 2);
    [X, Y] = ndgrid(X, Y)
    myIm_x  = private_checkerboard_x(n_u, cell_width)
    myIm_x  = interpn(X, Y, myIm_x, vx, vy, "linear")
    # myIm_x(isnan(myIm_x)) = nan_value;
    # gx1     = circshift(myIm_x, [-1, 0]) - myIm_x;
    # gx2     = circshift(myIm_x, [0, -1]) - myIm_x;
    # image_gradient ----------------------------------------------------------
    nExtend     = 0
    myIm_x      = bmImExtend(myIm_x, nExtend)
    gx          = bmImGradient(myIm_x)
    # TODO(matlab-line): gx1         = gx(:, :, 1);
    # TODO(matlab-line): gx2         = gx(:, :, 2);
    gx1         = bmImCrope(gx1, np.shape(gx1), np.shape(gx1) - 2*nExtend)
    gx2         = bmImCrope(gx2, np.shape(gx2), np.shape(gx2) - 2*nExtend)
    # TODO(matlab-line): gx          = sqrt(gx1.^2 + gx2.^2);
    # END_image_gradient ------------------------------------------------------
    # gx        = double(gx >= 0.5);
    myIm_y  = private_checkerboard_y(n_u, cell_width)
    myIm_y  = interpn(X, Y, myIm_y, vx, vy, "linear")
    # myIm_y(isnan(myIm_y)) = nan_value;
    # gy1     = circshift(myIm_y, [-1, 0]) - myIm_y;
    # gy2     = circshift(myIm_y, [0, -1]) - myIm_y;
    # image_gradient ----------------------------------------------------------
    nExtend     = 0
    myIm_y      = bmImExtend(myIm_y, nExtend)
    gy          = bmImGradient(myIm_y)
    # TODO(matlab-line): gy1         = gy(:, :, 1);
    # TODO(matlab-line): gy2         = gy(:, :, 2);
    gy1         = bmImCrope(gy1, np.shape(gy1), np.shape(gy1) - 2*nExtend)
    gy2         = bmImCrope(gy2, np.shape(gy2), np.shape(gy2) - 2*nExtend)
    # TODO(matlab-line): gy          = sqrt(gy1.^2 + gy2.^2);
    # END_image_gradient ------------------------------------------------------
    # gy        = double(gy >= 0.5);
    # TODO(matlab-line): myIm                = sqrt(gx.^2 + gy.^2);
    # myIm(1:end, 1)      = 0;
    # myIm(1:end, end)    = 0;
    # myIm(1, 1:end)      = 0;
    # myIm(end, 1:end)    = 0;
    # TODO(matlab-line): myIm(myIm < 0.3)    = 0;
    myIm                = min(0.5, myIm)
    m                   = (myIm > 0)
    myIm_r      = 0*myIm
    myIm_g      = 2*myIm
    myIm_b      = 0*myIm
    myIm_rgb    = cat(3, myIm_r, myIm_g, myIm_b)
    # TODO(matlab-control): if ~isempty(backGroundIm)
    backGroundIm = np.abs(backGroundIm)
    backGroundIm = backGroundIm - min(backGroundIm.ravel())
    backGroundIm = backGroundIm/max(backGroundIm.ravel())
    # TODO(matlab-line): b_r     = backGroundIm; b_r(m) = 0;
    # TODO(matlab-line): b_g     = backGroundIm; b_g(m) = 0;
    # TODO(matlab-line): b_b     = backGroundIm; b_b(m) = 0;
    b_rgb   = cat(3, b_r, b_g, b_b)
    myIm_rgb    = myIm_rgb + b_rgb
    figure
    image(myIm_rgb)
    # TODO(matlab-line): axis image

def private_checkerboard_x(n_u, cell_width):
    myOne       = np.ones(cell_width, 1)
    myZero      = np.zeros(cell_width, 1)
    myOneZero   = cat(1, myOne, myZero)
    myColumn = []
    # TODO(matlab-control): for i = 1:ceil(  n_u(1, 1)/(2*cell_width)  )
    myColumn = cat(1, myColumn, myOneZero)
    # TODO(matlab-line): myColumn    = myColumn(1:n_u(1, 1), 1);
    myIm_x      = repmat(myColumn, [1, n_u(1, 2)])
    return myIm_x

def private_checkerboard_y(n_u, cell_width):
    myOne       = np.ones(1, cell_width)
    myZero      = np.zeros(1, cell_width)
    myOneZero   = cat(2, myOne, myZero)
    myRow = []
    # TODO(matlab-control): for i = 1:ceil(  n_u(1, 2)/(2*cell_width)  )
    myRow = cat(2, myRow, myOneZero)
    # TODO(matlab-line): myRow       = myRow(1, 1:n_u(1, 2));
    myIm_y      = repmat(myRow, [n_u(1, 1), 1])
    return myIm_y
