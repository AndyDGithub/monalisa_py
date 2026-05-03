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

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(x, y, myString, markersize=myMarkerSize)
    ax.set_xlabel('Y')
    ax.set_ylabel('X')
    ax.invert_xaxis()
    ax.axis('image')
    plt.show()

    # No plotting is performed; the function exists purely as a
    # placeholder for compatibility with MATLAB scripts.
    # The returned dictionary is hidden from the public API but
    # could be useful for debugging in the future.
    return None
