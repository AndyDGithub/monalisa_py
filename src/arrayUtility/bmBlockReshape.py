import numpy as np


def bmBlockReshape(argIn, N_u):
    if isinstance(argIn, list):
        return [bmBlockReshape(item, N_u) for item in argIn]
    if isinstance(argIn, np.ndarray) and argIn.dtype == object:
        out = np.empty_like(argIn)
        for i, item in enumerate(argIn.ravel()):
            out.ravel()[i] = bmBlockReshape(item, N_u)
        return out
    argIn = np.asarray(argIn)
    if argIn.size == 0:
        return np.array([])
    N_u = np.array(N_u).ravel().astype(int)
    nCh = argIn.size // int(np.prod(N_u))
    return argIn.reshape(list(N_u) + [nCh])
