from __future__ import annotations
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.varargin.bmVarargin import bmVarargin

from src.arrayUtility.bmCol import bmCol
from src.image123.bmImGrid import bmImGrid


def bmImReg_deformField_to_positionField(v, n_u, X, Y, Z, varargin):
    """Strict deterministic baseline port from MATLAB."""
    circular_option = bmVarargin(varargin)
    if not circular_option:
        circular_option = True

    n_u = n_u[:, 0]
    imDim = len(n_u)

    v = bmBlockReshape(v, n_u)

    p = np.zeros_like(v, dtype=np.single)

    if imDim > 1:
        X, Y, Z = bmImGrid(n_u, X, Y, Z)

    if imDim == 1:
        X = bmCol(np.arange(1, n_u[0] + 1))

        p[:, 0] = v[:, 0] + X[:, 0]

        if circular_option:
            p[:, 0] = np.mod(v[:, 0] + X[:, 0], n_u[0]) + 1
            p[:, 0] = private_replace_smaller(p[:, 0], 1)
            p[:, 0] = private_replace_larger(p[:, 0], n_u[0])

    elif imDim == 2:
        p[:, :, 0] = v[:, :, 0] + X
        p[:, :, 1] = v[:, :, 1] + Y

        if circular_option:
            p[:, :, 0] = np.mod(p[:, :, 0] - 1, n_u[0]) + 1
            p[:, :, 1] = np.mod(p[:, :, 1] - 1, n_u[1]) + 1
            p[:, :, 0] = private_replace_smaller(p[:, :, 0], 1)
            p[:, :, 1] = private_replace_smaller(p[:, :, 1], 1)
            p[:, :, 0] = private_replace_larger(p[:, :, 0], n_u[0])
            p[:, :, 1] = private_replace_larger(p[:, :, 1], n_u[1])

    elif imDim == 3:
        p[:, :, :, 0] = v[:, :, :, 0] + X
        p[:, :, :, 1] = v[:, :, :, 1] + Y
        p[:, :, :, 2] = v[:, :, :, 2] + Z

        if circular_option:
            p[:, :, :, 0] = np.mod(p[:, :, :, 0] - 1, n_u[0]) + 1
            p[:, :, :, 1] = np.mod(p[:, :, :, 1] - 1, n_u[1]) + 1
            p[:, :, :, 2] = np.mod(p[:, :, :, 2] - 1, n_u[2]) + 1
            p[:, :, :, 0] = private_replace_smaller(p[:, :, :, 0], 1)
            p[:, :, :, 1] = private_replace_smaller(p[:, :, :, 1], 1)
            p[:, :, :, 2] = private_replace_smaller(p[:, :, :, 2], 1)
            p[:, :, :, 0] = private_replace_larger(p[:, :, :, 0], n_u[0])
            p[:, :, :, 1] = private_replace_larger(p[:, :, :, 1], n_u[1])
            p[:, :, :, 2] = private_replace_larger(p[:, :, :, 2], n_u[2])

    return p


def private_replace_smaller(p, c):
    q = p
    m = (q < c)
    q[m] = c
    return q


def private_replace_larger(p, c):
    q = p
    m = (q > c)
    q[m] = c
    return q
