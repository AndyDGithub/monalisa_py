import numpy as np


def bmColReshape(argIn, argSize):
    if isinstance(argIn, list):
        return [bmColReshape(item, argSize) for item in argIn]
    if isinstance(argIn, np.ndarray) and argIn.dtype == object:
        out = np.empty_like(argIn)
        for i, item in enumerate(argIn.ravel()):
            out.ravel()[i] = bmColReshape(item, argSize)
        return out
    argIn = np.asarray(argIn)
    nPt = int(np.prod(np.array(argSize).ravel()))
    nCh = argIn.size // nPt
    return argIn.reshape(nPt, nCh)
