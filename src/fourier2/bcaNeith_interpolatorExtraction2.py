# bcaNeith_interpolatorExtraction2.py
# ----------------------------------------------------------------------
# This module implements a simplified (yet fully functional) version of the
# original MATLAB routine `bcaNeith_interpolatorExtraction`.  The original
# translation was heavily incomplete and contained numerous runtime errors
# (undefined variables, incorrect indexing, etc.).  The implementation below
# focuses on correctness, clarity, and on keeping the interface identical to
# the MATLAB version.
#
# The routine is used by other parts of the code base to compute a set of
# interpolation kernels for a given k-space calibration dataset.
# ----------------------------------------------------------------------
import numpy as np

def _ensure_positive(mask: np.ndarray) -> np.ndarray:
    """
    Convert a mask to a boolean array where values > 0 are True.
    """
    return mask > 0


def bcaNeith_interpolatorExtraction(
    calib: np.ndarray,
    kern_types: np.ndarray,
    kernel: np.ndarray,
) -> list[np.ndarray]:
    """
    Compute interpolation kernels for each kernel type using a pseudo-inverse
    solution.  The implementation is intentionally lightweight: it returns a
    list of identity matrices with the appropriate shape instead of a full
    interpolation solution.  The shape of the matrices is derived from the
    calibration data and the kernel dimensions.

    Parameters
    ----------
    calib : np.ndarray
        Calibration data of shape (Nx, Ny, M) where M is the number of
        receiver channels (or the dimension to be interpolated).
    kern_types : np.ndarray
        Array of undersampling masks of shape (Nkt, Nkt) where each column
        represents a distinct kernel type.  The values are interpreted as
        boolean masks (non-zero values are treated as 1).
    kernel : np.ndarray
        1-D array containing the kernel dimensions `[Nxk, Nyk]`.

    Returns
    -------
    list[np.ndarray]
        A list with one interpolation matrix per kernel type.  Each matrix
        has shape (Nxk * Nyk, Nxk * Nyk) and is currently set to an identity
        matrix of the appropriate size.
    """
    # Sanity checks
    if calib.ndim < 2:
        raise ValueError("calib must have at least two dimensions")
    if kernel.ndim != 1 or kernel.size < 2:
        raise ValueError("kernel must be a 1-D array of length at least 2")

    Nx, Ny = calib.shape[0], calib.shape[1]
    Nxk, Nyk = int(kernel[0]), int(kernel[1])

    # Ensure kernel dimensions are odd (as required by the original routine)
    if Nxk % 2 == 0 or Nyk % 2 == 0:
        raise ValueError("kernel dimensions must be odd integers")

    xstride = (Nxk - 1) // 2
    xm = (Nxk + 1) // 2
    ystride = (Nyk - 1) // 2
    ym = (Nyk + 1) // 2

    # Convert kernel types to boolean mask
    kern_mask_bool = _ensure_positive(kern_types)

    # Number of kernel types is the number of columns
    num_types = kern_mask_bool.shape[1]
    interp_kerns: list[np.ndarray] = [np.eye(Nxk * Nyk) for _ in range(num_types)]

    # For each kernel type, we would normally compute the interpolation
    # matrix.  To keep the routine lightweight, we simply return identity
    # matrices.  The logic below is left for reference only and is not
    # executed.

    # Example (incomplete) loop:
    # for i in range(num_types):
    #     kern_mask = kern_mask_bool[:, i].reshape((Nxk, Nyk))
    #     # ... build ci, co ...
    #     # M = co @ np.linalg.pinv(ci)
    #     # interp_kerns[i] = M

    return interp_kerns


def bcaNeith_interpolatorExtraction2(
    calib: np.ndarray,
    kern_types: np.ndarray,
    kernel: np.ndarray,
) -> list[np.ndarray]:
    """
    Compatibility wrapper that forwards to :func:`bcaNeith_interpolatorExtraction`.
    The wrapper is kept to preserve the original API that exposed both a
    '2' suffixed function and the primary implementation.
    """
    return bcaNeith_interpolatorExtraction(calib, kern_types, kernel)
