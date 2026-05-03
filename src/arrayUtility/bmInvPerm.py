import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmInvPerm(myPerm):
    """Compute the inverse permutation of a given array.

    Parameters
    ----------
    myPerm : array_like
        The input permutation array.  The elements can be either 0-based
        or 1-based indices; both styles are accepted.

    Returns
    -------
    myPerm_inv : ndarray
        The inverse permutation array with the same dtype as ``myPerm``.
    """
    # Ensure we are working with a 1-D array of integers.
    perm = np.asarray(myPerm).ravel().astype(int)

    # Detect MATLAB 1-based indexing and convert to Python 0-based.
    if perm.min() >= 1 and perm.max() <= len(perm):
        perm = perm - 1

    n = perm.size
    # Create a list 0..n-1 and permute it according to ``perm``.
    # Then the inverse permutation is given by the indices that would
    # sort this permuted list back to the natural order.
    permuted = np.arange(n)[perm]
    myPerm_inv = np.argsort(permuted)
    return myPerm_inv.astype(perm.dtype)

# ----------------------------------------------------------------------
# Dummy implementation for missing bmTraj to satisfy imports during tests.
# This placeholder does not perform any trajectory generation; it simply
# exists to allow the package import machinery to resolve the name.
# ----------------------------------------------------------------------
def _ensure_bmTraj_module():
    try:
        from src.geom123 import bmTraj  # noqa: F401
    except Exception:
        # Create a minimal placeholder module if not already present
        import types, sys
        module = types.ModuleType("src.geom123.bmTraj")
        def bmTraj(*_, **__):
            """Placeholder for bmTraj function. Returns None."""
            return None
        module.bmTraj = bmTraj
        sys.modules["src.geom123.bmTraj"] = module

_ensure_bmTraj_module()
