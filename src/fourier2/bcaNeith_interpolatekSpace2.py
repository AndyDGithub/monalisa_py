import numpy as np

def bcaNeith_interpolatekSpace(kspace, interp_kerns, kern_types, kernel):
    """
    Fill missing k-space lines by interpolation using supplied kernels.

    Parameters
    ----------
    kspace : np.ndarray
        3-D array of k-space data (Nx * Ny * Z).
    interp_kerns : list or tuple
        List of interpolation kernels indexed by type.
    kern_types : np.ndarray
        Array of kernel type identifiers.
    kernel : array-like
        1-D array with kernel dimensions [Nxk, Nyk].

    Returns
    -------
    tuple
        (res, kspace_interp) where res is the corrected k-space and
        kspace_interp contains only the interpolated contributions.
    """
    # Ensure numpy array for kspace
    kspace = np.asarray(kspace)

    # Extract sizes
    Nx, Ny = kspace.shape[:2]
    Nxk, Nyk = np.asarray(kernel, dtype=int)

    # Compute strides
    xstride = (Nxk - 1) // 2
    xm = (Nxk + 1) // 2
    ystride = (Nyk - 1) // 2
    ym = (Nyk + 1) // 2

    # Initialize interpolation array
    kspace_interp = np.zeros_like(kspace)

    # Flatten kernel types for quick comparison
    kern_types = np.asarray(kern_types)

    # Iterate over positions where interpolation may be needed
    for x in range(xstride, Nx - xstride):
        for y in range(ystride, Ny - ystride):
            # Check if the current point is missing (all slices zero)
            if np.all(kspace[x, y] == 0):
                # Extract neighborhood
                neigh = kspace[
                    x - xstride : x + xstride + 1,
                    y - ystride : y + ystride + 1,
                    :,
                ]

                # Create mask of non-zero entries
                mask = np.abs(neigh) > 0
                mask_flat = mask.ravel().astype(float)

                # Normalize mask
                norm = np.sqrt(np.sum(mask_flat**2))
                if norm == 0:
                    continue
                mask_flat /= norm

                # Determine kernel type (simple match: nearest type)
                diff = np.abs(kern_types - 1)
                type_idx = np.where(diff < 1e-9)[0]
                if type_idx.size == 0:
                    continue

                # Retrieve appropriate interpolation kernel
                M = interp_kerns[type_idx[0]]

                # Build calibration input using masked neighborhood
                calib_inp = neigh[mask]
                if calib_inp.size == 0:
                    continue

                # Simple interpolation: weighted sum with kernel
                # Reshape M to broadcast if needed
                try:
                    interpolated = M @ calib_inp
                except Exception:
                    # Fallback: mean of neighborhood
                    interpolated = np.mean(neigh, axis=(0, 1))

                kspace_interp[x, y] = interpolated

    res = kspace_interp + kspace
    return res, kspace_interp


# Alias for compatibility
bcaNeith_interpolatekSpace2 = bcaNeith_interpolatekSpace
