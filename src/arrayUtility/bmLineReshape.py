import numpy as np


def bmLineReshape(argIn, argSize):
    if isinstance(argIn, list):
        return [bmLineReshape(item, argSize) for item in argIn]
    if isinstance(argIn, np.ndarray) and argIn.dtype == object:
        out = np.empty_like(argIn)
        for i, item in enumerate(argIn.ravel()):
            out.ravel()[i] = bmLineReshape(item, argSize)
        return out
    argIn = np.asarray(argIn)
    argSize = np.array(argSize).ravel().astype(int)
    nCh = int(argSize[0])
    N = int(argSize[1])
    nLine = argIn.size // nCh // N
    return argIn.reshape(nCh, N, nLine)
