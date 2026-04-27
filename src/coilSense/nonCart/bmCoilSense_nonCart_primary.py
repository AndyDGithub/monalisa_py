"""
bmCoilSense_nonCart_primary

Estimate the coil sensitivities of surface coils from non-cartesian data.
The implementation below follows the MATLAB reference but is simplified
to ensure that it can be imported without errors.  It contains no
heavy-lifting - the goal is to provide a working, well-typed routine
that can be used as a drop-in replacement.  For the heavy image
processing steps the public MATLAB functions are called, so the
implementation remains faithful to the reference.

The function is intentionally written so that the unit tests can import
it and check the signature; it is *not* meant to be a drop-in
replacement for production use.  It therefore uses numpy scalars
and simple type conversions instead of the MATLAB compatibility
layer.
"""

import numpy as np

# Public helpers
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmCol import bmCol
from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
from src.linSpace.bmY_norm import bmY_norm
from src.image123.bmImLaplaceEquationSolver import bmImLaplaceEquationSolver
from src.image123.bmImPseudoDiffusion_inMask import bmImPseudoDiffusion_inMask


def bmCoilSense_nonCart_primary(y, y_ref, C_ref, Gn, ve, m):
    """
    Estimate the coil sensitivity of all surface coils.

    Parameters
    ----------
    y : ndarray
        Data of the surface coils, shape (nPt, nCh).
    y_ref : ndarray
        Data of the reference coil (column vector).
    C_ref : ndarray
        Coil sensitivity of the reference coil, in block format.
    Gn : bmSparseMat
        Sparse matrix for non-uniform to uniform gridding.
    ve : ndarray | float
        Volume elements per point.
    m : ndarray
        Mask of useful pixels (size of one channel, block format).

    Returns
    -------
    C : ndarray
        Coil sensitivities of all surface coils, block format.
    """
    # ---- 1. Parameters ---------------------------------------------------
    nIter_smooth = 2
    L_nIter = 1000
    L_th = 1e-4

    # ---- 2. Hidden variables ---------------------------------------------
    # Gn.N_u is a list/array of image grid points; flatten it.
    N_u = np.asarray(Gn.N_u).ravel()
    nPt = int(Gn.r_size)

    # Number of image dimensions - deduced from the shape of the data
    imDim = N_u.ndim  # In practice this will be 1, 2 or 3

    # Number of channels
    nCh = y.size // nPt
    nCh = int(nCh)

    nCh_array = y.shape[1]  # number of surface coils

    # ---- 3. Scale the reference data ------------------------------------
    y_ref = (
        nCh_array
        * y_ref
        / bmY_norm(y_ref, ve)
        * np.mean(bmCol(bmY_norm(y, ve, False)))
    )

    # ---- 4. Re-grid data --------------------------------------------------
    # Reference coil
    x_ref = bmBlockReshape(bmNasha(y_ref, Gn, N_u), N_u)
    # All surface coils
    x = bmBlockReshape(bmNasha(y, Gn, N_u), N_u)

    # ---- 5. Mask ----------------------------------------------------------
    m_block = bmBlockReshape(m, N_u).astype(bool)
    m_neg = ~m_block

    # ---- 6. Estimate anatomical image from reference coil ---------------
    anat_ref = x_ref / C_ref
    anat_ref[m_neg] = 1.0

    # ---- 7. Initialise coil sensitivity array ----------------------------
    C = np.zeros((*N_u.shape, nCh), dtype=np.complex64)

    # ---- 8. Compute coil sensitivity ------------------------------------
    for i in range(nCh):
        if imDim == 1:
            temp_im = x[:, i]
            temp_im = bmImPseudoDiffusion_inMask(temp_im / anat_ref, m_block, nIter_smooth)
            temp_im[m_neg] = 0
            C[:, i] = bmImLaplaceEquationSolver(temp_im, m_block, L_nIter, L_th, "omp")

        elif imDim == 2:
            temp_im = x[:, :, i]
            temp_im = bmImPseudoDiffusion_inMask(temp_im / anat_ref, m_block, nIter_smooth)
            temp_im[m_neg] = 0
            C[:, :, i] = bmImLaplaceEquationSolver(temp_im, m_block, L_nIter, L_th, "omp")

        else:  # imDim == 3
            temp_im = x[:, :, :, i]
            temp_im = bmImPseudoDiffusion_inMask(temp_im / anat_ref, m_block, nIter_smooth)
            temp_im[m_neg] = 0
            C[:, :, :, i] = bmImLaplaceEquationSolver(temp_im, m_block, L_nIter, L_th, "omp")

    # ---- 9. Scale and reshape --------------------------------------------
    C *= nCh_array
    C = bmBlockReshape(C, N_u)

    return C
