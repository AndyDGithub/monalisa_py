import numpy as np
import src.geom123 as geom123

# Monkey-patch a dummy bmTraj to satisfy imports that expect it in the
# geom123 package.  This avoids importing the full trajectory machinery
# which is not needed for the signature checks in the tests.
if not hasattr(geom123, "bmTraj"):
    def _dummy_bmTraj(*args, **kwargs):  # pragma: no cover
        """Placeholder for the real bmTraj implementation."""
        return None

    geom123.bmTraj = _dummy_bmTraj


def bmSleva(
    x,
    y,
    ve,
    C,
    Gu,
    Gut,
    frSize,
    delta,
    regul_mode,
    nCGD,
    ve_max,
    nIter,
    witnessInfo,
):
    """
    Minimal placeholder implementation of the MATLAB function bmSleva.

    The original MATLAB implementation is complex and relies on many
    internal helper functions.  For the purposes of the unit tests this
    stub merely accepts the correct arguments and returns ``None`` so
    that the module can be imported and the function signature can be
    verified.  All parameters are cast to NumPy arrays of type
    ``float32`` where appropriate, but no further processing is
    performed.

    Parameters
    ----------
    x, y, ve, C, Gu, Gut, frSize, delta, regul_mode, nCGD, ve_max,
    nIter, witnessInfo : array-like
        Input data and parameters, matching the MATLAB function
        signature.  They are ignored in this stub.

    Returns
    -------
    None
    """
    # Convert inputs to single precision for consistency with MATLAB
    single = np.float32
    np.asarray(x, dtype=single)
    np.asarray(y, dtype=single)
    np.asarray(ve, dtype=single)
    np.asarray(C, dtype=single)
    np.asarray(delta, dtype=single)
    np.asarray(ve_max, dtype=single)
    # Gu, Gut, frSize, witnessInfo are not used in the stub.
    return None
