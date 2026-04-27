"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmCol import bmCol
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmPermuteToPoint import bmPermuteToPoint
from src.image2.m.bmImDeformField_hardThresholding2 import bmImDeformField_hardThresholding2
from src.varargin.bmVarargin import bmVarargin
from third_part.matlab_compat.matlab_native import repmat, save, single

from src.optim.bmBackGradient_nT import circshift

from src.sparseMat.m.bmSparseMat_vec import error
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# chain_type :      'curr_to_prev'      or
# 'curr_to_next'      or
# 'prev_to_curr'      or
# 'next_to_curr'      or
# 'curr_to_first'     or
# 'first_to_curr'

import numpy as np

def unknown_function():
    n_u,
    chain_type,
    nIter,
    nSmooth,
    arg_name,
    # TODO(matlab-line): varargin)
    maxImVal = 255;  # ----------------------------------------- magic number
    [myMask, maxPixDisplacement] = bmVarargin(varargin)
    x = bmBlockReshape(x, n_u)
    imDim           = np.shape(n_u.ravel(), 1)
    nCell           = np.shape(x.ravel(), 1)
    imDeformField   = cell(nCell, 1)
    im_out          = cell(nCell, 1)
    # TODO(matlab-control): if ~isempty(myMask)
    # TODO(matlab-control): for i = 1:nCell
    # TODO(matlab-line): x{i} = x{i}.*myMask;
    myMask = repmat(myMask.ravel(), [1, imDim])
    myMask = bmBlockReshape(myMask, n_u)
    # TODO(matlab-control): for i = 1:nCell
    v_reg = []
    i_minus_1 = mod(i-2, nCell) + 1
    i_plus_1  = mod(i  , nCell) + 1
    im_first    = single(private_smooth(x[1],         nSmooth))
    im_curr     = single(private_smooth(x[i],         nSmooth))
    im_prev     = single(private_smooth(x[i_minus_1], nSmooth))
    im_next     = single(private_smooth(x[i_plus_1],  nSmooth))
    [im_first, min_first, max_first]    = private_rescale(im_first, maxImVal)
    [im_curr,  min_curr,  max_curr]     = private_rescale(im_curr,  maxImVal)
    [im_prev,  min_prev,  max_prev]     = private_rescale(im_prev,  maxImVal)
    [im_next,  min_next,  max_next]     = private_rescale(im_next,  maxImVal)
    # TODO(matlab-control): if strcmp(chain_type,        'curr_to_prev')
    [v_reg, tmp_im]     = imregdemons(im_curr, im_prev, [nIter, fix(nIter/2), fix(nIter/4)])
    tmp_im              = tmp_im*max_curr/maxImVal + min_curr
    # TODO(matlab-control): elseif strcmp(chain_type,    'curr_to_next')
    [v_reg, tmp_im]     = imregdemons(im_curr, im_next, [nIter, fix(nIter/2), fix(nIter/4)])
    tmp_im              = tmp_im*max_curr/maxImVal + min_curr
    # TODO(matlab-control): elseif strcmp(chain_type,    'prev_to_curr')
    [v_reg, tmp_im]     = imregdemons(im_prev, im_curr, [nIter, fix(nIter/2), fix(nIter/4)])
    tmp_im              = tmp_im*max_prev/maxImVal + min_prev
    # TODO(matlab-control): elseif strcmp(chain_type,    'next_to_curr')
    [v_reg, tmp_im]     = imregdemons(im_next, im_curr, [nIter, fix(nIter/2), fix(nIter/4)])
    tmp_im              = tmp_im*max_next/maxImVal + min_next
    # TODO(matlab-control): elseif strcmp(chain_type,    'curr_to_first')
    # TODO(matlab-control): if i == 1
    v_reg = []
    # TODO(matlab-control): elseif i > 1
    [v_reg, tmp_im] = imregdemons(im_curr, im_first, [nIter, fix(nIter/2), fix(nIter/4)])
    tmp_im          = tmp_im*max_curr/maxImVal + min_curr
    # TODO(matlab-control): elseif strcmp(chain_type,    'first_to_curr')
    # TODO(matlab-control): if i == 1
    v_reg = []
    # TODO(matlab-control): elseif i > 1
    [v_reg, tmp_im] = imregdemons(im_first, im_curr, [nIter, fix(nIter/2), fix(nIter/4)])
    tmp_im          = tmp_im*max_first/maxImVal + min_first
    # TODO(matlab-control): else
    error("bmImDeformField_thirdPart : ""chain_type"" is unknown. ")
    # TODO(matlab-line): return;
    # TODO(matlab-control): if ~isempty(v_reg)
    v_reg = private_flip_x_y(squeeze(v_reg))
    im_out[i] = tmp_im
    v_reg               = bmBlockReshape(v_reg, n_u)
    # TODO(matlab-control): if ~isempty(myMask)
    # TODO(matlab-line): v_reg           = v_reg.*myMask;
    # TODO(matlab-control): if ~isempty(maxPixDisplacement)
    v_reg           = bmImDeformField_hardThresholding2(v_reg, n_u, maxPixDisplacement)
    v_reg               = bmPermuteToPoint(v_reg, n_u)
    imDeformField[i]    = v_reg
    varargout[1] = im_out
    # TODO(matlab-control): if ~isempty(arg_name)
    save(arg_name,  "imDeformField",        "-v7.3")
    save([arg_name, "_im_out"], "im_out",   "-v7.3")

def private_flip_x_y(v_in):
    v_out        = squeeze(v_in)
    temp_size    = bmCol(np.shape(v_out)).T
    temp_imDim   = np.shape(temp_size.ravel(), 1) - 1
    # TODO(matlab-line): temp_N_u     = temp_size(1, 1:temp_imDim);
    v_out        = bmColReshape(v_out, temp_N_u)
    # TODO(matlab-line): temp_x       = v_out(:, 1);
    # TODO(matlab-line): v_out(:, 1)  = v_out(:, 2);
    # TODO(matlab-line): v_out(:, 2)  = temp_x;
    v_out        = bmBlockReshape(v_out, temp_N_u)
    return v_out

def private_smooth(im_in, nSmooth):
    N_u = np.shape(im_in)
    imDim = np.shape(N_u.ravel(), 1)
    im_out = im_in
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-control): for i = 1:nSmooth
    im_out = (im_out + circshift(im_out, [1, 0])    + circshift(im_out, [-1, 0]))/3
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-control): for i = 1:nSmooth
    im_out = (im_out + circshift(im_out, [1, 0])    + circshift(im_out, [0, 1])    + circshift(im_out, [-1, 0])   + circshift(im_out, [0, -1]))/5
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-control): for i = 1:nSmooth
    im_out = (im_out + circshift(im_out, [1, 0, 0]) + circshift(im_out, [0, 1, 0]) + circshift(im_out, [0, 0, 1]) + circshift(im_out, [-1, 0, 0]) + circshift(im_out, [0, -1, 0]) + circshift(im_out, [0, 0, -1]) )/7
    return im_out

def private_rescale(arg_im, arg_val):
    out     = np.abs(arg_im)
    out_min = min(out.ravel())
    out     = out - out_min
    out_max = max(out.ravel())
    out     = out/out_max
    out     = out*arg_val
    return (out, out_min, out_max)

def bmImDeformFieldChain_imRegDemons23():
    return unknown_function()
