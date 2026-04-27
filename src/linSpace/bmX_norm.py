from src.varargin.bmVarargin import bmVarargin
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
import numpy as np


def bmX_norm(x, d_u, varargin):
    collapse_flag = bmVarargin(varargin)
    # if isempty(collapse_flag)
    if collapse_flag is None:
        collapse_flag = False
    # if ndims(x) > 2
    if x.ndim > 2:
        raise ValueError("This function is for 2Dim arrays only.")
    dV = np.prod(d_u)
    # if size(x, 1) > size(x, 2)
    if x.shape[0] > x.shape[1]:
        n = np.sqrt(np.abs(np.sum(np.conj(x) * (x * dV), axis=1)))
    else:
        n = np.sqrt(np.abs(np.sum(np.conj(x) * (x * dV), axis=2)))
    # if collapse_flag
    if collapse_flag:
        n = np.sqrt(np.sum(n ** 2))

    return n
