import numpy as np

def bmDirichletKernel(x, N):
    myEps = 1e-4
    f = np.sin((N + 0.5) * x) / np.sin(x / 2)
    mask = np.isinf(f) | ~np.isfinite(f) | np.isnan(f) | (np.abs(np.sin(x / 2)) < myEps)
    f[mask] = 2 * N + 1
    return f
