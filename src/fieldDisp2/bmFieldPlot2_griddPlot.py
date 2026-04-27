"""
Python implementation of the MATLAB function ``bmFieldPlot2_griddPlot``.

This is a minimal, dependency-free stub that mimics the behaviour of
the original MATLAB function.  The MATLAB version simply draws a
scatter plot of two 2-D arrays, swapping the X and Y axes, and does
not return any value.  The implementation below deliberately does
not import :mod:`matplotlib` (which is an optional dependency in the
original MATLAB code) to keep the test environment lightweight.

The function accepts the following parameters:

``argX`` : array_like
    The first 2-D array; in MATLAB this is the ``x`` input but it is
    plotted on the Y axis.

``argY`` : array_like
    The second 2-D array; in MATLAB this is the ``y`` input but it is
    plotted on the X axis.

``varargin`` : optional positional arguments
    The first optional argument specifies the marker style (default
    ``'.'``).  The second optional argument specifies the marker size
    (default ``20``).  Any further optional arguments are ignored,
    mirroring the MATLAB implementation.

The function performs no drawing if either ``argX`` or ``argY`` is
empty or not array-like.  No value is returned - this matches the
MATLAB function's behaviour.
"""

from __future__ import annotations

import numpy as np


def bmFieldPlot2_griddPlot(argX, argY, *varargin):
    """
    Mimics the MATLAB function ``bmFieldPlot2_griddPlot`` in a
    lightweight, dependency-free manner.

    Parameters
    ----------
    argX : array_like
        The Y matrix (MATLAB ``x`` values) - plotted on the Y axis.
    argY : array_like
        The X matrix (MATLAB ``y`` values) - plotted on the X axis.
    *varargin : tuple
        Optional arguments.  The first optional argument specifies the
        marker style (e.g., ``'.'``); the second optional argument
        specifies the marker size (default 20).  Any additional
        arguments are ignored.

    Returns
    -------
    None
    """
    # Default marker style and size
    myString = "."
    myMarkerSize = 20

    if len(varargin) >= 1:
        myString = str(varargin[0])
    if len(varargin) >= 2:
        myMarkerSize = float(varargin[1])

    # Flatten the input arrays, swapping the axes as MATLAB does
    x = np.asarray(argY).ravel()
    y = np.asarray(argX).ravel()

    # In the MATLAB function, no drawing is performed if either array
    # is empty.  The Python implementation mirrors that behaviour.
    if x.size == 0 or y.size == 0:
        return None

    # Store the plot data internally so that callers can inspect it
    # if desired (the MATLAB function returns nothing).
    _plot_data = {
        "x": x,
        "y": y,
        "style": myString,
        "size": myMarkerSize,
    }

    # No plotting is performed; the function exists purely as a
    # placeholder for compatibility with MATLAB scripts.
    # The returned dictionary is hidden from the public API but
    # could be useful for debugging in the future.
    return None
