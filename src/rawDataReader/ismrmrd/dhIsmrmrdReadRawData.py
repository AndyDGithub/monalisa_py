import numpy as np
from src.arrayUtility import bmBlockReshape  # Import statement added to resolve ModuleNotFoundError

from third_part.matlab_compat.matlab_native import single

def dhIsmrmrdReadRawData(obj, flagSS, flagExcludeSI):
    argFile = obj.argFile
    acquisitionParams = obj.acquisitionParams
    nCh = acquisitionParams.nCh
    N = acquisitionParams.N
    nSeg = acquisitionParams.nSeg
    nShot = acquisitionParams.nShot
    nEcho = acquisitionParams.nEcho
    nLine = acquisitionParams.nLine
    nShot_off = acquisitionParams.nShot_off

    readouts = complex(np.zeros([N, nCh, nLine]))

    myData = h5read(argFile, "/dataset/data")
    raw_data = myData['data']

    for i in range(nLine):
        acq = raw_data[i]
        acq = np.reshape(acq, [2, N, nCh])  # [complex, N, nCh]
        readouts[:, :, i] = squeeze(acq[0, :, :] + 1j * acq[1, :, :])

    readouts = single(readouts)

    if nEcho == 1:
        readouts = bmBlockReshape(readouts, [2, 3, 4], [1, 2, 3])
        if flagSS and nShot_off > 0:
            readouts = np.delete(readouts, np.s_[0:nShot_off], 3)
            nShot -= nShot_off
        if flagExcludeSI:
            readouts = np.delete(readouts, 0, 2)
            nSeg -= 1

        readouts = readouts.reshape([nCh, N, nSeg * nShot])

    elif nEcho == 2:
        raise ValueError('bmTwix_data : nEcho == 2, case not implemented, yet. But we have to do it for Giulia''s data ! ')
    else:
        raise ValueError('bmTwix_data : case not implemented. ')

    return readouts
