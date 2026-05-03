from __future__ import annotations
import numpy as np


class _TranslationTransform:
    def __init__(self):
        self.t = None


def bmImReg_getInitialTranslationTransform_estimate_2(imRef, imMov, X=None, Y=None, Z=None):
    """
    Estimate initial translation transform by brute-force circular shift search
    on a downsampled 48x48(x48) grid.
    """
    imRef = np.asarray(imRef, dtype=float)
    imMov = np.asarray(imMov, dtype=float)

    n_u   = np.array(imRef.shape)
    imDim = len(n_u)
    s     = np.ones(imDim, dtype=int) * 48  # magic number

    # Downsample via simple slicing (crude but matches MATLAB intent)
    def _resize(im, s):
        from scipy.ndimage import zoom
        factors = [si / ni for si, ni in zip(s, im.shape)]
        return zoom(np.abs(im), factors, order=1)

    a = _resize(imRef, s)
    b = _resize(imMov, s)

    f = n_u / s.astype(float)

    if imDim == 2:
        r = np.zeros(s, dtype=float)
        for i in range(s[0]):
            for j in range(s[1]):
                imShift = np.roll(np.roll(a, i, axis=0), j, axis=1)
                r[i, j] = np.sum(np.abs(imShift - b))
    elif imDim == 3:
        r = np.zeros(s, dtype=float)
        for i in range(s[0]):
            for j in range(s[1]):
                for k in range(s[2]):
                    imShift = np.roll(np.roll(np.roll(a, i, 0), j, 1), k, 2)
                    r[i, j, k] = np.sum(np.abs(imShift - b))
    else:
        raise NotImplementedError(f"imDim={imDim} not supported")

    min_idx = np.unravel_index(np.argmin(r), r.shape)
    t = np.array(min_idx, dtype=float) * f

    T = _TranslationTransform()
    T.t = t.reshape(-1, 1)
    return T
