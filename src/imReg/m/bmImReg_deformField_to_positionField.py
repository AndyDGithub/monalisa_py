"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.image123.bmImGrid import bmImGrid
from src.varargin.bmVarargin import bmVarargin
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmImReg_deformField_to_positionField(v, n_u, X, Y, Z, varargin):
    circular_option = bmVarargin(varargin)
    # TODO(matlab-control): if isempty(circular_option)
    circular_option = True
    n_u     = n_u.ravel().T
    imDim   = np.shape(n_u.ravel(), 1)
    v       = bmBlockReshape(v, n_u)
    p       = np.zeros(np.shape(v), "single")
    # TODO(matlab-control): if imDim > 1
    [X, Y, Z] = bmImGrid(n_u, X, Y, Z)
    # TODO(matlab-control): if imDim == 1
    # TODO(matlab-line): X           = bmCol(1:n_u(1, 1));
    # TODO(matlab-line): p(:, 1)     = v(:, 1) + X(:, 1);
    # TODO(matlab-control): if circular_option
    # TODO(matlab-line): p(:, 1)     = mod( v(:, 1) + X(:, 1), n_u(1, 1) ) + 1;
    # TODO(matlab-line): p(:, 1) = private_replace_smaller(p(:, 1), 1);
    # TODO(matlab-line): p(:, 1) = private_replace_larger(p(:, 1),  n_u(1, 1));
    # TODO(matlab-control): elseif imDim == 2
    # TODO(matlab-line): p(:, :, 1)  = v(:, :, 1) + X;
    # TODO(matlab-line): p(:, :, 2)  = v(:, :, 2) + Y;
    # TODO(matlab-control): if circular_option
    # TODO(matlab-line): p(:, :, 1)  = mod( p(:, :, 1) - 1, n_u(1, 1) ) + 1;
    # TODO(matlab-line): p(:, :, 2)  = mod( p(:, :, 2) - 1, n_u(1, 2) ) + 1;
    # TODO(matlab-line): p(:, :, 1) = private_replace_smaller(p(:, :, 1), 1);
    # TODO(matlab-line): p(:, :, 2) = private_replace_smaller(p(:, :, 2), 1);
    # TODO(matlab-line): p(:, :, 1) = private_replace_larger(p(:, :, 1), n_u(1, 1));
    # TODO(matlab-line): p(:, :, 2) = private_replace_larger(p(:, :, 2), n_u(1, 2));
    # TODO(matlab-control): elseif imDim == 3
    # TODO(matlab-line): p(:, :, :, 1)  = v(:, :, :, 1) + X;
    # TODO(matlab-line): p(:, :, :, 2)  = v(:, :, :, 2) + Y;
    # TODO(matlab-line): p(:, :, :, 3)  = v(:, :, :, 3) + Z;
    # TODO(matlab-control): if circular_option
    # TODO(matlab-line): p(:, :, :, 1)  = mod( p(:, :, :, 1) - 1, n_u(1, 1) ) + 1;
    # TODO(matlab-line): p(:, :, :, 2)  = mod( p(:, :, :, 2) - 1, n_u(1, 2) ) + 1;
    # TODO(matlab-line): p(:, :, :, 3)  = mod( p(:, :, :, 3) - 1, n_u(1, 3) ) + 1;
    # TODO(matlab-line): p(:, :, :, 1) = private_replace_smaller(p(:, :, :, 1), 1);
    # TODO(matlab-line): p(:, :, :, 2) = private_replace_smaller(p(:, :, :, 2), 1);
    # TODO(matlab-line): p(:, :, :, 3) = private_replace_smaller(p(:, :, :, 3), 1);
    # TODO(matlab-line): p(:, :, :, 1) = private_replace_larger(p(:, :, :, 1), n_u(1, 1));
    # TODO(matlab-line): p(:, :, :, 2) = private_replace_larger(p(:, :, :, 2), n_u(1, 2));
    # TODO(matlab-line): p(:, :, :, 3) = private_replace_larger(p(:, :, :, 3), n_u(1, 3));
    return p

def private_replace_smaller(p, c):
    q = p
    m = (q < c)
    # TODO(matlab-line): q(m) = c;
    return q

def private_replace_larger(p, c):
    q = p
    m = (q > c)
    # TODO(matlab-line): q(m) = c;
    return q
