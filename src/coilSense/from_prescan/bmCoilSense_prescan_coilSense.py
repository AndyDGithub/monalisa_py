import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmZero import bmZero
from src.image123.bmImLaplaceEquationSolver import bmImLaplaceEquationSolver
from third_part.matlab_compat.matlab_native import logical, repmat, single

from src.image123.bmImPseudoDiffusion_inMask import bmImPseudoDiffusion_inMask

def bmCoilSense_prescan_coilSense(x_body, x_surface, m, n_u):
    # bmCoilSense_prescan_coilSense - Estimate coil sensitivity maps from pre-scan images.
    # Usage:
    # C = bmCoilSense_prescan_coilSense(x_body, x_surface, m, n_u)
    # Inputs:
    # x_body    : Body coil prescan image (1D, 2D, or 3D).
    # x_surface : Surface (array) coil prescan image (1D, 2D, or 3D).
    # m         : Mask segmenting the non-zero signal volume, with dimensions matching the images.
    # n_u       : Image size excluding channels (e.g., [96, 96] or [64, 56, 32]).
    # Outputs:
    # C         : Estimated coil sensitivity maps (complex single).

    L_nIter = 1000
    L_th = 1e-4
    x_body_ind = 1

    n_u = n_u.flatten()
    imDim = len(n_u)
    nCh = int(x_surface.size / np.prod(n_u))

    x_body = single(bmColReshape(x_body, n_u))
    rms_body = single(bmColReshape(np.sqrt((x_body**2).sum(axis=1)), n_u))
    x_body = x_body[:, x_body_ind]

    x_surface = single(bmColReshape(x_surface, n_u))

    m = logical(bmColReshape(m, n_u))
    m_neg = ~m
    m_rep = repmat(m.flatten(), [1, nCh])
    m_neg_rep = ~m_rep

    x_body = bmBlockReshape(x_body, n_u)
    rms_body = bmBlockReshape(rms_body, n_u)
    x_surface = bmBlockReshape(x_surface, n_u)
    m = bmBlockReshape(m, n_u)
    m_neg = bmBlockReshape(m_neg, n_u)

    x_body_norm = np.sqrt((x_body**2).sum(axis=1))
    x_surface_norm = bmColReshape(x_surface, n_u)
    x_surface_norm = np.sqrt((x_surface_norm**2).sum(axis=(1 if imDim == 1 else (1, 2) if imDim == 2 else (1, 2, 3))))
    x_surface_norm = np.mean(x_surface_norm, axis=1 if imDim == 1 else (1, 2) if imDim == 2 else (1, 2, 3))

    x_body /= x_body_norm[:, np.newaxis]
    rms_body /= x_body_norm[:, np.newaxis]
    x_surface /= x_surface_norm

    x_body[m_neg] = 1
    rms_body[m_neg] = 1

    C_body_abs = bmImPseudoDiffusion_inMask(np.abs(x_body) / rms_body, m, L_nIter)
    C_body_phi = np.zeros_like(C_body_abs)
    C_body = C_body_abs * np.exp(1j * C_body_phi)
    C_body[m_neg] = 0

    C_body = bmImLaplaceEquationSolver(C_body, m, L_nIter, L_th, 'omp')

    anat = x_body / C_body
    anat[m_neg] = 1

    C = bmZero([n_u, nCh], 'complex_single')

    for i in range(nCh):
        if imDim == 1:
            temp_im = x_surface[:, i]
            temp_im = bmImPseudoDiffusion_inMask(temp_im / anat, m, L_nIter)
            temp_im[m_neg] = 0
            C[:, i] = bmImLaplaceEquationSolver(temp_im, m, L_nIter, L_th, 'omp')

        elif imDim == 2:
            temp_im = x_surface[:, :, i]
            temp_im = bmImPseudoDiffusion_inMask(temp_im / anat, m, L_nIter)
            temp_im[m_neg] = 0
            C[:, :, i] = bmImLaplaceEquationSolver(temp_im, m, L_nIter, L_th, 'omp')

        elif imDim == 3:
            temp_im = x_surface[:, :, :, i]
            temp_im = bmImPseudoDiffusion_inMask(temp_im / anat, m, L_nIter)
            temp_im[m_neg] = 0
            C[:, :, :, i] = bmImLaplaceEquationSolver(temp_im, m, L_nIter, L_th, 'omp')

    C = bmBlockReshape(C, n_u)
    return C
