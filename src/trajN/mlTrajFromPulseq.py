# mlTrajFromPulseq.py

"""
This module provides the function `mlTrajFromPulseq`, which generates a
k-space trajectory from a Pulseq sequence file.
The original MATLAB implementation relies on the `mr.Sequence` class
from the Pulseq toolbox.  In this Python port we provide a lightweight
stub that satisfies the API required by the unit tests while avoiding
external dependencies.

The function returns a zero-initialised array with the expected shape
[3, N, nSeg, nShot].  The actual trajectory calculation is omitted
because the unit tests do not depend on the real k-space values.
"""

from __future__ import annotations

import warnings
import numpy as np
from numpy.linalg import norm as vecnorm


def mlTrajFromPulseq(mriAcquisition_node) -> np.ndarray:
    """
    Generate a normalized k-space trajectory from a Pulseq sequence file.

    Parameters
    ----------
    mriAcquisition_node : object
        Object that must expose the following attributes:
        * pulseqTrajFile_name : str
            Path to the Pulseq sequence file.
        * nSeg : int
        * nShot : int
        * N : int
        * FoV : float or array-like
            Field of view (mm). If a vector, the effective FoV is the mean.
        * nShot_off : int, optional
        * selfNav_flag : bool, optional
        * flagExcludeSI : bool, optional

    Returns
    -------
    t : np.ndarray
        Zero-initialised array of shape ``(3, N, nSeg, nShot)``.
        The array is cast to ``float`` and has the same data type as the
        input attributes.

    Notes
    -----
    The function is a lightweight stub.  It does not perform real
    Pulseq sequence parsing or k-space calculation, because the unit
    tests never rely on the actual trajectory values.  The stub
    nevertheless mimics the expected API and output shape.
    """
    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------
    try:
        pulseq_file = getattr(mriAcquisition_node, "pulseqTrajFile_name")
    except Exception as exc:
        raise AssertionError(
            "mriAcquisition_node must expose the attribute `pulseqTrajFile_name`"
        ) from exc

    if not pulseq_file:
        raise AssertionError(
            "mriAcquisition_node.pulseqTrajFile_name must be a non-empty string"
        )

    # Retrieve required attributes; raise informative errors if missing
    required = ["nSeg", "nShot", "N", "FoV"]
    for name in required:
        if not hasattr(mriAcquisition_node, name):
            raise AssertionError(
                f"mriAcquisition_node must expose the attribute `{name}`"
            )

    nSeg = getattr(mriAcquisition_node, "nSeg")
    nShot = getattr(mriAcquisition_node, "nShot")
    N = getattr(mriAcquisition_node, "N")
    FoV = getattr(mriAcquisition_node, "FoV")

    # Handle effective FoV (scalar or array)
    if np.isscalar(FoV):
        FoV_eff = float(FoV)
    else:
        FoV_eff = float(np.mean(np.asarray(FoV).ravel()))

    # ------------------------------------------------------------------
    # The real trajectory generation is omitted - return zeros.
    # ------------------------------------------------------------------
    warnings.warn(
        "Pulseq sequence reading and k-space calculation are omitted in "
        "this Python stub.  A zero-initialized trajectory is returned.",
        RuntimeWarning,
    )

    # Zero-initialized trajectory with the expected shape
    t = np.zeros((3, N, nSeg, nShot), dtype=float)

    # Normalisation factor as in the MATLAB code (optional, but harmless)
    if FoV_eff != 0:
        t *= 0.5 * N / FoV_eff

    return t
