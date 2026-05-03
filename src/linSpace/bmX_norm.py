from __future__ import annotations
import numpy as np
from src.varargin.bmVarargin import bmVarargin


def bmX_norm(x, d_u, varargin):
    """Strict deterministic baseline port from MATLAB."""
    collapse_flag = bmVarargin(varargin)
    if not collapse_flag:
        collapse_flag = False

    if x.ndim > 2:
        raise ValueError('This function is for 2D arrays only.')

    dV = np.prod(d_u)
    if x.shape[0] > x.shape[1]:
        n = np.sqrt(np.abs(np.sum(np.conj(x) * (x * dV), axis=1)))
    else:
        n = np.sqrt(np.abs(np.sum(np.conj(x) * (x * dV), axis=2)))

    if collapse_flag:
        n = np.sqrt(np.sum(n**2))

    return n
