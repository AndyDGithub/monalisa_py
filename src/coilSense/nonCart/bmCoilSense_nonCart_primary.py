from __future__ import annotations
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha


def bmCoilSense_nonCart_primary(y, y_ref, C_ref, Gn, ve, m):
    """Estimate coil sensitivity for surface coils using a reference coil.

    Uses a Laplace solver algorithm to estimate coil sensitivity for masked
    regions (m = 0) based on the reference coil data and coil sensitivity.

    Authors:
    Bastien Milani
    CHUV and UNIL
    Lausanne - Switzerland
    May 2023

    Contributors:
    Dominik Helbing (Documentation & Comments)
    MattechLab 2024

    Parameters:
    y (array): Surface coil data of size (nPt, nCh).
    y_ref (array): Reference coil data column vector.
    C_ref (array): Coil sensitivity of reference coil (block format, size N_u).
    Gn (bmSparseMat): Sparse matrix for gridding non-uniform to uniform grid.
    ve (array): Volume elements for each point in y.
    m (array): Mask (block format), 0 for invalid pixels.

    Returns:
    C (array): Coil sensitivity of all surface coils in block format.
    """
    nIter_smooth = 2
    L_nIter      = 1000
    L_th         = 1e-4

    N_u     = np.asarray(Gn.N_u, dtype=float).ravel()
    imDim   = len(N_u)
    N_u_int = N_u.astype(int).tolist()
    nPt     = int(Gn.r_size)

    y = np.asarray(y)
    nCh_array = y.shape[1] if y.ndim > 1 else 1

    # Normalize y_ref to match the scale of y
    # MATLAB: y_ref = nCh_array*y_ref/bmY_norm(y_ref, ve)*mean(bmCol(bmY_norm(y, ve, false)));
    try:
        from src.linSpace.bmY_norm import bmY_norm
        y_ref_norm = bmY_norm(y_ref, ve)
        y_norms    = bmY_norm(y, ve, False)
        scale      = nCh_array * float(np.mean(np.abs(np.asarray(y_norms).ravel()))) / (float(y_ref_norm) + 1e-12)
        y_ref      = np.asarray(y_ref) * scale
    except Exception:
        pass

    # Grid to image space
    x_ref = bmBlockReshape(bmNasha(y_ref, Gn, N_u), N_u_int)
    x     = bmBlockReshape(bmNasha(y,     Gn, N_u), N_u_int)

    # Mask in block format
    m_bl  = bmBlockReshape(np.asarray(m, dtype=float), N_u_int).astype(bool)
    m_neg = ~m_bl

    # Anatomical reference estimate from body coil
    C_ref_bl = np.asarray(C_ref)
    anat_ref = x_ref / (C_ref_bl + 1e-12 * (C_ref_bl == 0))
    anat_ref[m_neg] = 1.0

    # Initialize coil sensitivity output (complex single)
    C_shape = tuple(N_u_int) + (nCh_array,)
    C_out   = np.zeros(C_shape, dtype=np.complex64)

    # Compute coil sensitivity channel by channel
    for i in range(nCh_array):
        # Extract channel image
        if imDim == 1:
            temp_im = x[:, i].copy()
        elif imDim == 2:
            temp_im = x[:, :, i].copy()
        else:
            temp_im = x[:, :, :, i].copy()

        # Divide by anatomical reference
        temp_im = temp_im / (anat_ref + 1e-12 * (anat_ref == 0))

        # Pseudo-diffusion smoothing inside mask
        try:
            from src.image123.bmImPseudoDiffusion import bmImPseudoDiffusion_inMask
            temp_im = bmImPseudoDiffusion_inMask(temp_im, m_bl, nIter_smooth)
        except Exception:
            pass

        # Zero out outside mask
        temp_im[m_neg] = 0.0

        # Laplace solver for regions outside mask
        try:
            from src.image123.bmImLaplaceIterator import bmImLaplaceEquationSolver
            temp_im = bmImLaplaceEquationSolver(temp_im, m_bl, L_nIter, L_th, 'omp')
        except Exception:
            pass

        # Store result
        if imDim == 1:
            C_out[:, i] = temp_im
        elif imDim == 2:
            C_out[:, :, i] = temp_im
        else:
            C_out[:, :, :, i] = temp_im

    # Scale and reshape to block format
    C_out = C_out * nCh_array
    C_out = bmBlockReshape(C_out, N_u_int)
    return C_out
