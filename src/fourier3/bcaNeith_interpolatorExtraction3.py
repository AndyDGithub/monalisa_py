"""Auto-generated from MATLAB source. Review manually before production use."""

import numpy as np
from scipy import linalg

def InterpolatorExtraction(calib, kern_types, kernel):
    Nx, Ny, Nz = calib.shape[0], calib.shape[1], calib.shape[2]
    Nxk, Nyk, Nzk = kernel

    xstride = (Nxk - 1) / 2
    xm = (Nxk + 1) / 2
    ystride = (Nyk - 1) / 2
    ym = (Nyk + 1) / 2
    zstride = (Nzk - 1) / 2
    zm = (Nzk + 1) / 2

    kern_types = kern_types > 0
    interp_kerns = []

    for i in range(kern_types.shape[1]):
        t = 1
        ci = []
        co = []
        kern_mask = np.reshape(kern_types[:, i], (Nxk, Nyk, Nzk))

        for x in range(1 + xstride, Nx - xstride):
            for y in range(1 + ystride, Ny - ystride):
                for iz in range(1 + zstride, Nz - zstride):
                    calib_inp = []
                    calib_out = []

                    for xx in range(-xstride, xstride + 1):
                        for yy in range(-ystride, ystride + 1):
                            for zz in range(-zstride, zstride + 1):
                                if kern_mask[xx + xm, yy + ym, zz + zm] > 0:
                                    calib_inp.append(calib[x + xx, y + yy, iz + zz])

                    if not calib_inp:
                        continue

                    ci_temp = np.array(calib_inp).reshape(-1, 1)
                    co_temp = np.array([calib[x, y, iz] for x in range(Nx) for y in range(Ny) for iz in range(Nz) if (x + xx, y + yy, iz + zz) not in calib_inp])

                    ci.append(ci_temp)
                    co.append(co_temp)
                    t += 1

        M = linalg.pinv(np.concatenate(ci, axis=1)) @ np.concatenate(co, axis=1)
        interp_kerns.append(M)

    return interp_kerns

def bcaNeith_interpolatorExtraction3(calib, kern_types, kernel):
    return InterpolatorExtraction(calib, kern_types, kernel)
