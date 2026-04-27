from src.arrayUtility.bmCol import bmCol
from src.arrayUtility.bmIsScalar import bmIsScalar
import numpy as np

def bmEuclideProd(x1, x2, H):
    if isinstance(x1[0], (list, np.ndarray)) and isinstance(x2[0], (list, np.ndarray)) and isinstance(H[0], (list, np.ndarray)):
        N = np.shape(x1[0].ravel(), 1)
        out = 0
        if bmIsScalar(H[0]):
            for i in range(N):
                out += np.real(bmCol(x1[i]).T * (H[i] * bmCol(x2[i])))
        else:
            for i in range(N):
                out += np.real(bmCol(x1[i]).T * (bmCol(H[i]) * bmCol(x2[i])))
    elif isinstance(x1[0], (list, np.ndarray)) and isinstance(x2[0], (list, np.ndarray)) and not isinstance(H[0], (list, np.ndarray)):
        N = np.shape(x1[0].ravel(), 1)
        out = 0
        if bmIsScalar(H):
            for i in range(N):
                out += np.real(bmCol(x1[i]).T * (H * bmCol(x2[i])))
        else:
            for i in range(N):
                out += np.real(bmCol(x1[i]).T * (bmCol(H) * bmCol(x2[i])))
    elif not isinstance(x1[0], (list, np.ndarray)) and not isinstance(x2[0], (list, np.ndarray)) and not isinstance(H[0], (list, np.ndarray)):
        if bmIsScalar(H):
            out = np.real(x1.ravel().T * (H * x2.ravel()))
        else:
            out = np.real(x1.ravel().T * (H * x2.ravel()))
    else:
        raise ValueError("In bmEuclideProd : case not implemented.")

    return out
