import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.fftpack import fftn, ifftn
from src.arrayUtility import bmBlockReshape  # Import statement for the missing module

def normalize(arr, norm_type='l2'):
    """ Normalize an array using the specified norm type. """
    return arr / np.linalg.norm(arr, ord=norm_type, axis=None)

def undersamp_shape(x, y, xstride, ystride):
    """ Return the undersampled shape based on stride and matrix size. """
    return (x - xstride) // xstride * 2 + 1, (y - ystride) // ystride * 2 + 1

def bcaNeith_interpolatekSpace3(kspace, interp_kerns, kern_types, kernel):
    Nx, Ny, Nz, Nc = np.shape(kspace)
    Nxk, Nyk, Nzk = kernel

    xstride = (Nxk - 1) / 2
    ystride = (Nyk - 1) / 2
    zstride = (Nzk - 1) / 2

    kspace_interp = np.zeros((Nx, Ny, Nz, Nc))

    for x in range(1 + xstride, Nx - xstride):
        for y in range(1 + ystride, Ny - ystride):
            for iz in range(1 + zstride, Nz - zstride):
                if np.abs(kspace[x, y, iz]) == 0:
                    continue

                kspace_kern = kspace[x - xstride:x + xstride + 1, y - ystride:y + ystride + 1, iz - zstride:iz + zstride + 1]
                kspace_kern_mask = np.abs(kspace_kern) > 0
                kspace_kern_mask = 1 * kspace_kern_mask.ravel()

                kspace_kern_mask = normalize(kspace_kern_mask, 'norm')
                type = np.where(np.abs((kern_types.T @ kspace_kern_mask) - 1) < 1e-9)[0]

                if len(type) == 0:
                    continue

                M = interp_kerns[type]
                calib_inp = []

                for xx in range(-xstride, xstride + 1):
                    for yy in range(-ystride, ystride + 1):
                        for zz in range(-zstride, zstride + 1):
                            if kern_mask[xx + xm, yy + ym, zz + zm] > 0:
                                calib_inp.append(kspace[x + xx, y + yy, iz + zz])

                kspace_interp[x, y, iz, :] = M @ np.array(calib_inp)

            res = kspace_interp + kspace
            return res, kspace_interp
