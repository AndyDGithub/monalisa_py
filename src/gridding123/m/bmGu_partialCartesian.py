# -*- coding: utf-8 -*-
"""
% Bastien Milani
% CHUV and UNIL
% Lausanne - Switzerland
% May 2023

Implementation of bmGu_partialCartesian translated from MATLAB.

The original MATLAB function reshapes an input array and selects rows
according to specified indices.

This module requires ``numpy`` and ``bmColReshape`` from the project.
"""

from __future__ import annotations

import numpy as np
from src.arrayUtility.bmColReshape import bmColReshape


def bmGu_partialCartesian(x, ind_u, N_u):
    """
    Reshape the input array ``x`` and select rows based on ``ind_u``.

    Parameters
    ----------
    x : np.ndarray
        Input array.
    ind_u : np.ndarray
        Indices of rows to select from the reshaped ``x``.
    N_u : np.ndarray
        New size for reshaping ``x``.

    Returns
    -------
    y : np.ndarray
        Selected rows from the reshaped array ``x``.
    """
    N_u = np.array(N_u.ravel().T, dtype=float)
    ind_u = np.array(ind_u.ravel(), dtype=int)
    x = bmColReshape(x, N_u)

    y = x[ind_u, :]

    return y
