# coding: utf-8
# Copyright (c) 2019-2022, M. S. K. J. van de Linde
# All rights reserved.
# BSD-3-Clause

# ==============================================================================
# bmCoilSense_nonCart_ref
# ==============================================================================
# The function is ported from the MATLAB version.

from __future__ import annotations

import numpy as np
from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
from src.imageN.bmRMS import bmRMS
from src.image123.bmImPseudoDiffusion_inMask import bmImPseudoDiffusion_inMask
from src.image123.bmImLaplaceEquationSolver import bmImLaplaceEquationSolver
from src.coilSense.nonCart.functions.matrices import bmColReshape, bmBlockReshape
from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
from src.imageN.bmRMS import bmRMS
from src.image123.bmImPseudoDiffusion_inMask import bmImPseudoDiffusion_inMask
from src.image123.bmImLaplaceEquationSolver import bmImLaplaceEquationSolver

def bmCoilSense_nonCart_ref(
    y: np.ndarray,
    Gn: object,
    m: np.ndarray,
    nSmooth_phi: int | None,
) -> tuple[list[np.complex64], np.ndarray]:
    """
    Computes the coil-sensitivity of the first reference coil for a non-Cartesian
    acquisition.

    Parameters
    ----------
    y : np.ndarray
        Raw k-space data as a 2-D array of complex values.  The first
        column corresponds to the first reference coil.
    Gn : object
        `bmCartesian_matlab` (the `bmMatfile` structure).  It contains
        a property `N_u` that holds the dimensions of the block format
        (e.g. [Nx, Ny, Nz] for 3-D).
    m : np.ndarray
        The mask with the same shape as the reference coil images
        (i.e. `N_u` dimensions).  It is used to indicate where the
        actual data points exist.
    nSmooth_phi : int | None
        Optional smoothing factor for the phase.  If ``None`` or ``[]`` a
        zero phase is assumed.

    Returns
    -------
    tuple[list[np.complex64], np.ndarray]
        * A column vector containing the reference coil image in single
          precision.
        * The estimated coil-sensitivity of that reference coil in block
          format (``N_u`` dimensions).
    """

    # -------------------------------------------------------------------------
    # 1. Solver and smoothing parameters
    # -------------------------------------------------------------------------
    L_nIter = 30   # iterations for Laplace solver
    L_th = 1e-5     # tolerance for Laplace solver
    nIter_smooth = 30  # pseudo-diffusion smoothing iterations

    # -------------------------------------------------------------------------
    # 2. Hidden variables - from `Gn`
    # -------------------------------------------------------------------------
    # Determine number of channels
    try:
        # In MATLAB the structure `Gn.N_u` is a vector of grid sizes.
        N_u = np.array(Gn.N_u, dtype=np.float64)  # shape: (len(Gn.N_u),)
    except AttributeError:
        raise ValueError("Gn must expose a `N_u` attribute with grid sizes.")

    # Number of channels - inferred from the shape of `y`
    nCh = y.shape[1] if y.ndim > 1 else 1

    # -------------------------------------------------------------------------
    # 3. Mask manipulation
    # -------------------------------------------------------------------------
    m_bool = np.asarray(m, dtype=bool)
    m_neg = ~m_bool

    # Replicate the mask for all channels
    m_rep = np.tile(m_bool.reshape(-1, 1), (1, nCh))

    # -------------------------------------------------------------------------
    # 4. Regrid raw data
    # -------------------------------------------------------------------------
    # Regrid the raw data using the basis functions
    # The result is in single precision
    k_space = bmNasha(y, Gn, N_u.astype(int))
    x_ch = bmColReshape(k_space, N_u.astype(int)).astype(np.float32)

    # Replace missing points with 1
    x_ch[m_neg.reshape(-1, 1)] = 1.0

    # Convert to block format - same shape as the reference coil image
    x_ch = bmBlockReshape(x_ch, N_u.astype(int))

    # -------------------------------------------------------------------------
    # 5. Compute RMS and initialise complex coil-sensitivity array
    # -------------------------------------------------------------------------
    myRMS = bmRMS(x_ch, N_u.astype(int))

    # Initialise coil-sensitivity array `C` - complex float32
    # Shape: N_u + (nCh,)
    C_shape = tuple(N_u) + (nCh,)
    z = np.zeros(C_shape, dtype=np.float32)
    C = z.astype(np.complex64)

    # -------------------------------------------------------------------------
    # 6. Loop over all reference coils
    # -------------------------------------------------------------------------
    imDim = len(N_u)
    for i in range(nCh):
        # For the i-th coil image (in block format)
        if imDim == 1:
            temp_a = x_ch[:, i]
        elif imDim == 2:
            temp_a = x_ch[..., i]
        elif imDim == 3:
            temp_a = x_ch[..., i]
        else:
            raise ValueError(f"Unsupported dimension {imDim} for reference coil.")

        # Pseudo-diffusion - magnitude and phase
        C_abs = bmImPseudoDiffusion_inMask(np.abs(temp_a) / myRMS, m_bool, nIter_smooth)
        if nSmooth_phi is not None:
            C_phi = np.angle(bmImPseudoDiffusion_inMask(temp_a, m_bool, nSmooth_phi))
        else:
            C_phi = np.zeros_like(temp_a, dtype=np.float32)

        temp_C = C_abs * np.exp(1j * C_phi)

        # Apply Laplace-equation solver
        # The algorithm string is only a placeholder in this implementation
        # but is kept for compatibility with the original MATLAB code.
        temp_C[m_neg] = 0.0
        C[..., i] = bmImLaplaceEquationSolver(temp_C, m_bool, L_nIter, L_th, "omp")

    # -------------------------------------------------------------------------
    # 7. Assemble outputs
    # -------------------------------------------------------------------------
    # Convert block format to column vector
    x_ch_col = bmColReshape(x_ch, N_u.astype(int))
    C_col = bmColReshape(C, N_u.astype(int))

    # Reference coil image and sensitivity (first coil)
    y_ref = y[:, 0].tolist()
    C_ref = C_col[:, 0]
    C_ref = bmBlockReshape(C_ref, N_u.astype(int))

    return y_ref, C_ref
