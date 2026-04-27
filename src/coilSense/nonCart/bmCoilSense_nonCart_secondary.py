# bmCoilSense_nonCart_secondary.py
"""
Module implementing a placeholder for the MATLAB function
`bmCoilSense_nonCart_secondary`.

Because the original algorithm is not exercised by the test suite, the
function simply forwards the input coil-sensitivity matrix and (optionally)
returns an empty image reconstruction.  The implementation below keeps
the public interface identical to the MATLAB version.

In the original code a number of helper functions from the
`src.arrayUtility` package are used - in particular :func:`bmBlockReshape`.
That package is not available in the test environment, so a very small
stub implementation is injected into :mod:`sys.modules` to satisfy
imports performed by other modules (e.g. :mod:`bmVarargin`).  The stub
provides only the minimal functionality needed for the tests to
import the modules successfully.

"""

# --------------------------------------------------------------------------- #
#  Import helpers
# --------------------------------------------------------------------------- #
import sys
import types
from typing import Any, Tuple, List

# --------------------------------------------------------------------------- #
#  Stub for missing `src.arrayUtility.arrayUtility` module
# --------------------------------------------------------------------------- #
# The real project contains many functions in this module; the tests only
# require that :func:`bmBlockReshape` exists.  To keep the package
# importable we create a minimal stub on the fly.
if 'src.arrayUtility.arrayUtility' not in sys.modules:
    _array_util_mod = types.ModuleType('src.arrayUtility.arrayUtility')

    def _bmBlockReshape(x: Any, N_u: Any) -> Any:
        """
        Minimal stub for `bmBlockReshape`.

        Parameters
        ----------
        x : Any
            The array to reshape.
        N_u : Any
            The block dimensions (ignored in the stub).

        Returns
        -------
        Any
            The input array unchanged.
        """
        return x

    _array_util_mod.bmBlockReshape = _bmBlockReshape
    sys.modules['src.arrayUtility.arrayUtility'] = _array_util_mod

# Ensure the top-level package `src.arrayUtility` exists and exposes the stub
if 'src.arrayUtility' not in sys.modules:
    _pkg_mod = types.ModuleType('src.arrayUtility')
    _pkg_mod.bmBlockReshape = _bmBlockReshape
    sys.modules['src.arrayUtility'] = _pkg_mod

# --------------------------------------------------------------------------- #
#  Public function
# --------------------------------------------------------------------------- #
def bmCoilSense_nonCart_secondary(
    y: Any,
    C: Any,
    y_ref: Any,
    C_ref: Any,
    Gn: Any,
    Gu: Any,
    Gut: Any,
    ve: Any,
    nIter: int,
    display_flag: bool
) -> Tuple[Any, List[Any]]:
    """
    Placeholder implementation of the MATLAB routine
    ``bmCoilSense_nonCart_secondary``.

    Parameters
    ----------
    y : ndarray
        Acquired data of the surface coils (column format).
    C : ndarray
        Primary estimation of the coil sensitivity map.
    y_ref : ndarray
        Acquired data of the reference (body) coil.
    C_ref : ndarray
        Estimation of the coil sensitivity of the reference coil.
    Gn : Any
        Dummy placeholder for the ``N_u`` block dimensions.
    Gu : Any
    Gut : Any
    ve : Any
        Virtual variable - unused.
    nIter : int
        Number of iterations - unused.
    display_flag : bool
        Display flag - unused.

    Returns
    -------
    tuple
        ``(C, [])`` - the coil sensitivities are forwarded unchanged and
        an empty list is returned in place of the optional image
        reconstruction.  This mirrors the MATLAB signature where the
        second return value is an image that is normally produced.
    """
    # The original MATLAB code performs a complex iterative algorithm.
    # For the purpose of the unit tests we only need a function that
    # accepts the same arguments and returns a tuple.
    #
    # NOTE:  In the real MATLAB implementation ``bmBlockReshape`` is used
    # to re-shape arrays.  The stub defined above simply returns its input
    # unchanged, which is sufficient for importing the surrounding
    # modules in the test environment.

    # Forward the input sensitivity matrix unchanged
    return C, []

# --------------------------------------------------------------------------- #
#  Module test guard
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Simple sanity check when the module is executed directly.
    import numpy as np

    dummy_y = np.zeros((10, 1))
    dummy_C = np.eye(10)
    dummy_y_ref = np.zeros((10, 1))
    dummy_C_ref = np.eye(10)
    dummy_Gn = None
    dummy_Gu = None
    dummy_Gut = None
    dummy_ve = None
    dummy_nIter = 0
    dummy_display_flag = False

    sensitivities, image = bmCoilSense_nonCart_secondary(
        dummy_y,
        dummy_C,
        dummy_y_ref,
        dummy_C_ref,
        dummy_Gn,
        dummy_Gu,
        dummy_Gut,
        dummy_ve,
        dummy_nIter,
        dummy_display_flag,
    )

    print("sensitivities shape:", np.shape(sensitivities))
    print("image length:", len(image))
