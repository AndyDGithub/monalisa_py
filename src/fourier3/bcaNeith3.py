"""Auto-generated from MATLAB source. Review manually before production use."""

from src.fourier3.bcaNeith_interpolatekSpace3 import bcaNeith_interpolatekSpace3
from src.fourier3.bcaNeith_interpolatorExtraction3 import bcaNeith_interpolatorExtraction3
from src.fourier3.bcaNeith_kernelTypeExtraction3 import bcaNeith_kernelTypeExtraction3

import numpy as np

def MATLABGrappa(kspace, calib, kern):
    kern = np.asarray(kern, dtype=int).reshape(-1)
    if not isKern(kern):
        raise ValueError('kern must contain 3 odd values strictly greater than 1')
    padsize = ((kern - 1) // 2).astype(int)
    pad_width = [(int(p), int(p)) for p in padsize[:3].tolist()]
    if np.ndim(kspace) > 3:
        pad_width.extend([(0, 0)] * (np.ndim(kspace) - 3))
    kspace_padded = np.pad(kspace, tuple(pad_width), mode='constant')

    kern_types = bcaNeith_kernelTypeExtraction3(kspace_padded, kern)
    interp_kerns = bcaNeith_interpolatorExtraction3(calib, kern_types, kern)
    res, _kspace_interp = bcaNeith_interpolatekSpace3(kspace_padded, interp_kerns, kern_types, kern)

    xpad, ypad, zpad = (int(padsize[0]), int(padsize[1]), int(padsize[2]))
    xs = slice(xpad, -xpad if xpad else None)
    ys = slice(ypad, -ypad if ypad else None)
    zs = slice(zpad, -zpad if zpad else None)
    return res[xs, ys, zs, ...]


def isKern(kern):
    values = np.asarray(kern, dtype=int).reshape(-1)
    if values.size != 3:
        return False
    if np.any(values <= 1):
        return False
    return bool(np.all(((values - 1) % 2) == 0))


def bcaNeith3(kspace, calib, kern):
    return MATLABGrappa(kspace, calib, kern)
