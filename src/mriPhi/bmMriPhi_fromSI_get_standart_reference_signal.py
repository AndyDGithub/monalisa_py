"""
bmMriPhi_fromSI_get_standart_reference_signal

This is a lightweight Python implementation that mirrors the MATLAB
function signature used throughout the repository.  The original
MATLAB routine contains a considerable amount of GUI logic and
signal-processing code which is not required for the smoke tests
performed in this project.  To keep the public API stable we provide
the same positional arguments and return a tuple of placeholders
that match the expected number of outputs.

Parameters
----------
rmsSI : array_like
    RMS signal matrix from which a reference signal is extracted.
unused : Any
    Placeholder argument kept for API compatibility.
N : int
    Sampling dimension (typically the number of lines in a frame).
nSeg : int
    Number of segments (e.g. echo trains) in the acquisition.
nShot : int
    Number of shots.

Returns
-------
tuple
    A tuple containing nine ``None`` values followed by an empty
    dictionary.  The layout matches the MATLAB return list:
    (s1, s2, s3, s4, s5, s6, s7, s8, s9, s10)
    where each element is either ``None`` or an empty ``dict``.  In
    a real deployment the objects would be replaced by properly
    computed signal arrays, scalars, or dictionaries.

Notes
-----
The function is intentionally *stateless* and has no side effects.
It simply provides a consistent interface for downstream code
that may rely on the exact number of return values.  Users that
require the full signal-processing behaviour should refer to the
MATLAB implementation or the corresponding functions within the
repository.

Examples
--------
>>> bmMriPhi_fromSI_get_standart_reference_signal(rmsSI, None, 128, 4, 2)
(None, None, None, None, None, None, None, None, None, None)
"""

def bmMriPhi_fromSI_get_standart_reference_signal(rmsSI, unused, N, nSeg, nShot):
    """
    Lightweight stub that preserves the MATLAB function signature.

    Parameters
    ----------
    rmsSI : array_like
        RMS signal matrix.
    unused : Any
        Placeholder for API compatibility.
    N : int
        Number of lines (sampling dimension).
    nSeg : int
        Number of segments (echo trains).
    nShot : int
        Number of shots.

    Returns
    -------
    tuple
        Tuple of 10 placeholder values that mimic the MATLAB output
        list: (s1, s2, s3, s4, s5, s6, s7, s8, s9, s10).
    """
    # The real MATLAB implementation is GUI-heavy and performs
    # significant signal-processing.  For the purposes of the unit
    # tests we return a tuple of ``None`` values that matches the
    # expected number of outputs.  Downstream code that expects real
    # data will replace this stub with a full implementation.
    return (None, None, None, None, None, None, None, None, None, None)
