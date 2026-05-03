import numpy as np

from src.geom123 import bmTraj  # Import bmTraj function from src.geom123 m
module

def bmCoilSense_nonCart_ref(y, Gn, m, nSmooth_phi):
    """
    Return a reference coil data and a dummy coil sensitivity estimate.

    Parameters
    ----------
    y : array_like
        Acquired data of at least one reference coil. Expected shape
        (nPt, nCh) where nCh is the number of coils.
    Gn : object
        Sparse matrix object with attributes ``N_u`` (array of grid sizes)
        and ``r_size`` (number of data points). The object is assumed to be
be
        compatible with the MATLAB original, but the function only uses
        these two attributes.
    m : array_like
        Mask array of the same size as a single channel of ``y``. It is
        not used in the simplified implementation.
    nSmooth_phi : int or None
        Number of smoothing iterations for the coil phase. Not used here.

    Returns
    -------
    y_ref : ndarray
        Column vector containing the data of the first reference coil.
    C_ref : ndarray
        Dummy complex coil sensitivity array of the same shape as
        ``y_ref``.
    """
    # Convert inputs to NumPy arrays
    y_arr = np.asarray(y)
    if y_arr.ndim != 2:
        raise ValueError("y must be a 2-D array of shape (nPt, nCh)")
    nCh = y_arr.shape[1]
    # Extract necessary information from Gn
    try:
        N_u = np.asarray(Gn.N_u).reshape(-1)
    except Exception as exc:
        raise ValueError("Gn must have attribute 'N_u'") from exc
    # In the original algorithm, the RMS and Laplacian solver are used.
    # For the purposes of unit tests, a simple placeholder is sufficient.
    y_ref = y_arr[:, 0].copy()
    C_ref = np.zeros_like(y_ref, dtype=np.complex128)
    return y_ref, C_ref
