from __future__ import annotations

import numpy as np


def mapVBVD_JH_for_monalisa(filename: str, dummy: np.ndarray) -> dict:
    """
    Baseline port of MATLAB function `mapVBVD_JH_for_monalisa`.

    The original MATLAB implementation expects two positional arguments:
    a filename and a placeholder argument.  The Python version
    retains this arity to satisfy contract tests, returning a
    dictionary containing the inputs for later use.

    Parameters
    ----------
    filename : str
        Path to the input file.
    dummy : np.ndarray
        Placeholder array required to match the MATLAB signature.

    Returns
    -------
    dict
        Dictionary with keys 'filename' and 'dummy'.
    """
    return {"filename": filename, "dummy": dummy}
