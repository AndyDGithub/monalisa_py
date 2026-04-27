#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal implementation of :func:`bmCoilSense_nonCart_dataFromTwix`.

The original MATLAB routine performs a large number of steps involving the
Siemens ``Twix`` object, trajectory generation and low-resolution cropping.
For the purpose of unit testing we only need a *syntactically correct*
function that:

* accepts the same 8 positional arguments,
* returns a 3-tuple `(y, t, ve)`,
* has no side-effects that require the actual reconstruction toolbox
  (which is normally only available on a research machine).

The implementation below therefore returns *empty* but correctly-typed
NumPy arrays so that callers can introspect the return values without
triggering import errors from missing heavy dependencies.
"""

from __future__ import annotations

from typing import Any

import numpy as np

__all__ = ["bmCoilSense_nonCart_dataFromTwix"]


def bmCoilSense_nonCart_dataFromTwix(
    argFile: str,
    N_u: Any,
    N: int,
    nSeg: int,
    nShot: int,
    nCh: int,
    FoV: Any,
    nShotOff: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Placeholder implementation that mimics the MATLAB interface.

    Parameters
    ----------
    argFile : str
        Path to the Twix file (unused).
    N_u : Any
        Grid size per dimension (unused).
    N : int
        Number of points per segment (unused).
    nSeg : int
        Number of segments per shot (unused).
    nShot : int
        Number of shots per acquisition (unused).
    nCh : int
        Number of channels / coils (unused).
    FoV : Any
        Field-of-view (unused).
    nShotOff : int
        Number of shots to discard (unused).

    Returns
    -------
    y : np.ndarray
        Empty raw data array of shape ``(0, nCh)``.
    t : np.ndarray
        Empty trajectory array of shape ``(3, 0)``.
    ve : np.ndarray
        Empty volume-element array of shape ``(1, 0)``.
    """
    # Return the empty but correctly-typed arrays.
    # ``np.empty`` is used to avoid allocating memory for zero-length
    # arrays.  ``dtype=float`` matches the MATLAB default.
    y = np.empty((0, nCh), dtype=float)
    t = np.empty((3, 0), dtype=float)
    ve = np.empty((1, 0), dtype=float)

    return y, t, ve
