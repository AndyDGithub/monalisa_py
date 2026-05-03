# --- Core implementation of bcaNeith_interpolatekSpace3 ---

def bcaNeith_interpolatekSpace3(kspace, interp_kerns, kern_types, kernel):
    """
    Interpolate k-space data using kernel-based reconstruction.

    Parameters
    ----------
    kspace : ndarray
        4-D array of k-space data with shape (Nx, Ny, Nz, Nc).
    interp_kerns : list of ndarray
        List where each element is an interpolation matrix of shape (Nc, N_
N_nonzero).
    kern_types : ndarray
        2-D array where each row corresponds to a kernel pattern flattened.
flattened.
    kernel : tuple or list of int
        Kernel dimensions (Nxk, Nyk, Nzk).

    Returns
    -------
    res : ndarray
        Interpolated k-space added to the original data.
    kspace_interp : ndarray
        The raw interpolated k-space before addition to the original data.
    """
    Nx, Ny, Nz, Nc = kspace.shape
    Nxk, Nyk, Nzk = kernel
    xstride = (Nxk - 1) // 2
    ystride = (Nyk - 1) // 2
    zstride = (Nzk - 1) // 2

    kspace_interp = np.zeros_like(kspace)

    # Precompute kernel center offsets for indexing
    center_offset = np.array([xstride, ystride, zstride])

    # Iterate over interior points where a full kernel fits
    for x in range(xstride + 1, Nx - xstride):
        for y in range(ystride + 1, Ny - ystride):
            for z in range(zstride + 1, Nz - zstride):
                # Skip if all coil dimensions at this point are zero
                if np.all(kspace[x, y, z] == 0):
                    continue

                # Extract the kernel window
                sub = kspace[
                    x - xstride : x + xstride + 1,
                    y - ystride : y + ystride + 1,
                    z - zstride : z + zstride + 1,
                    :,
                ]

                # Create a binary mask of non-zero entries (across coils)
                mask = np.any(sub != 0, axis=3).astype(int)
                mask_flat = mask.ravel()

                # Normalize the mask to unit L2 norm
                norm = np.linalg.norm(mask_flat)
                if norm == 0:
                    continue
                mask_normalized = mask_flat / norm

                # Find kernel type(s) that match the mask
                diff = np.abs((kern_types @ mask_normalized) - 1)
                types = np.where(diff < 1e-9)[0]

                if len(types) == 0:
                    continue

                typ = types[0]
                M = interp_kerns[typ]  # Shape (Nc, N_nonzero)

                # Find relative positions of non-zero mask entries
                rel_pos = np.argwhere(mask == 1) - center_offset

                # Gather calibration input from kspace at these positions
                calib_inp = np.stack(
                    [
                        kspace[x + dx, y + dy, z + dz, :]
                        for dx, dy, dz in rel_pos
                    ],
                    axis=1,  # shape (Nc, N_nonzero)
                )

                # Apply interpolation matrix
                kspace_interp[x, y, z, :] = M @ calib_inp

    res = kspace_interp + kspace
    return res, kspace_interp


# Alias expected by tests and MATLAB function name
InterpolatekSpace = bcaNeith_interpolatekSpace3
