import numpy as np


def _core(kspace, kernel):
    """Extract unique normalized 2D kernel masks around missing samples."""
    kspace = np.asarray(kspace)
    kernel = np.asarray(kernel).ravel().astype(int)
    if kernel.size < 2:
        raise ValueError("kernel must contain two odd dimensions [Nxk, Nyk].")

    Nxk, Nyk = int(kernel[0]), int(kernel[1])
    if Nxk % 2 == 0 or Nyk % 2 == 0:
        raise ValueError("kernel dimensions must be odd.")

    Nx, Ny = kspace.shape[:2]
    xstride = (Nxk - 1) // 2
    ystride = (Nyk - 1) // 2

    types = []
    for i in range(xstride, Nx - xstride):
        for j in range(ystride, Ny - ystride):
            if abs(kspace[i, j]) != 0:
                continue

            kspace_kern = kspace[i - xstride:i + xstride + 1, j - ystride:j + ystride + 1]
            mask = (np.abs(kspace_kern) > 0).astype(np.float64).reshape(-1, order="F")
            nrm = np.linalg.norm(mask)
            if nrm > 0:
                mask = mask / nrm

            if not types:
                types.append(mask)
                continue

            mat = np.column_stack(types)
            corr = mat.T @ mask
            if not np.any(np.abs(corr - 1.0) < 1e-9):
                types.append(mask)

    if not types:
        return np.empty((Nxk * Nyk, 0), dtype=np.float64)
    return np.column_stack(types)


def bcaNeith_kernelTypeExtraction2(kspace, kernel):
    """Compatibility wrapper (2D-specific function name)."""
    return _core(kspace, kernel)


def bcaNeith_kernelTypeExtraction(kspace, kernel):
    """MATLAB-compatible public name expected by callers."""
    return _core(kspace, kernel)
