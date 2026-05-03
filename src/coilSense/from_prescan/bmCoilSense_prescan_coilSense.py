from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmZero import bmZero
from src.image123.bmImLaplaceEquationSolver import bmImLaplaceEquationSolver
from src.image123.bmImPseudoDiffusion_inMask import bmImPseudoDiffusion_inMask
from src.imageN.bmRMS import bmRMS
from third_part.matlab_compat.matlab_native import logical, repmat, single
def bmCoilSense_prescan_coilSense(x_body, x_surface, m, n_u):
    """Estimate coil sensitivity maps from pre-scan images.

    Parameters
    ----------
    x_body : np.ndarray
        Body coil pre-scan image (1-D, 2-D or 3-D).
    x_surface : np.ndarray
        Surface coil pre-scan image (1-D, 2-D or 3-D).
    m : np.ndarray
        Mask of the non-zero signal volume. Must have the same spatial
        dimensions as the images.
    n_u : array-like
        Image size excluding the channel dimension, e.g. [96, 96] or
        [64, 56, 32].

    Returns
    -------
    C : np.ndarray
        Estimated coil sensitivity maps (complex, single precision).
    """
    # Magic constants from MATLAB
    L_nIter = 1000
    L_th = 1e-4
    x_body_ind = 0          # 0-based index for MATLAB's 1
    nIter_smooth = 2

    # Ensure inputs are numpy arrays
    n_u = np.asarray(n_u).reshape(1, -1)  # 1-row array
    imDim = n_u.shape[1]
    prod_n_u = int(np.prod(n_u))
    nCh = int(x_surface.size // prod_n_u)

    # 1. Reshape and normalize the body coil image
    x_body = single(bmColReshape(x_body, n_u))
    rms_body = single(bmColReshape(bmRMS(x_body, n_u), n_u))
    x_body = x_body[:, x_body_ind]  # select the first column

    # 2. Reshape surface coil image
    x_surface = single(bmColReshape(x_surface, n_u))

    # 3. Prepare mask
    m = logical(bmColReshape(m, n_u))
    m_neg = ~m
    m_rep = repmat(m.reshape(-1, 1), (1, nCh))
    m_neg_rep = ~m_rep

    # 4. Block reshape to spatial dimensions
    x_body = bmBlockReshape(x_body, n_u)
    rms_body = bmBlockReshape(rms_body, n_u)
    x_surface = bmBlockReshape(x_surface, n_u)
    m = bmBlockReshape(m, n_u)
    m_neg = bmBlockReshape(m_neg, n_u)

    # 5. Normalization
    # Compute norms over all spatial elements for each channel
    x_body_flat = x_body.reshape(-1, nCh)
    rms_body_flat = rms_body.reshape(-1, nCh)
    x_surface_flat = x_surface.reshape(-1, nCh)

    x_body_norm = np.sqrt(np.sum(np.abs(x_body_flat) ** 2, axis=0))
    x_surface_norm = np.sqrt(np.sum(np.abs(x_surface_flat) ** 2, axis=0))
    x_surface_norm = np.mean(x_surface_norm, axis=0)

    x_body = x_body / x_body_norm
    rms_body = rms_body / x_body_norm
    x_surface = x_surface / x_surface_norm

    # 6. Handle negative mask
    x_body[m_neg] = 1
    rms_body[m_neg] = 1

    # 7. Body coil sensitivity estimation
    C_body_abs = bmImPseudoDiffusion_inMask(
        np.abs(x_body) / rms_body, m, nIter_smooth
    )
    C_body_phi = np.zeros_like(C_body_abs)
    C_body = C_body_abs * np.exp(1j * C_body_phi)
    C_body[m_neg] = 0
    C_body = bmImLaplaceEquationSolver(C_body, m, L_nIter, L_th, "omp")

    # 8. Anatomical image
    anat = x_body / C_body
    anat[m_neg] = 1

    # 9. Allocate output array
    C = bmZero([*n_u, nCh], "complex_single")

    # 10. Iterate over surface coils
    for i in range(nCh):
        if imDim == 1:
            temp_im = x_surface[:, i]
        elif imDim == 2:
            temp_im = x_surface[:, :, i]
        elif imDim == 3:
            temp_im = x_surface[:, :, :, i]
        else:
            raise ValueError(f"Unsupported dimension: {imDim}")

        temp_im = bmImPseudoDiffusion_inMask(
            temp_im / anat, m, nIter_smooth
        )
        temp_im[m_neg] = 0
        C_shape = C.shape
        if imDim == 1:
            C[:, i] = bmImLaplaceEquationSolver(
                temp_im, m, L_nIter, L_th, "omp"
            )
        elif imDim == 2:
            C[:, :, i] = bmImLaplaceEquationSolver(
                temp_im, m, L_nIter, L_th, "omp"
            )
        elif imDim == 3:
            C[:, :, :, i] = bmImLaplaceEquationSolver(
                temp_im, m, L_nIter, L_th, "omp"
            )

    # 11. Reshape back to block format
    C = bmBlockReshape(C, n_u)

    return C
