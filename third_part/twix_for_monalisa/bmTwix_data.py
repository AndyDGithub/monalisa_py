import numpy as np
from third_part.matlab_compat.matlab_native import permute
from src.arrayUtility.bmBlockReshape import bmBlockReshape

def bmTwix_data(myTwix, myMriAcquisition_node):
    N               = myMriAcquisition_node.N
    nSeg            = myMriAcquisition_node.nSeg
    nShot           = myMriAcquisition_node.nShot
    nCh             = myMriAcquisition_node.nCh
    nEcho           = myMriAcquisition_node.nEcho
    selfNav_flag    = myMriAcquisition_node.selfNav_flag
    nShot_off       = myMriAcquisition_node.nShot_off
    roosk_flag      = myMriAcquisition_node.roosk_flag
    y_raw   = myTwix.image.unsorted()

    # If nEcho == 1
    if nEcho == 1:
        y_raw = permute(y_raw, [2, 1, 3])
        y_raw = np.reshape(y_raw, [nCh, N, nSeg, nShot])

        # Remove self-navigation data (if selfNav_flag is True)
        if selfNav_flag:
            y_raw[:, :, 1, :] = []

        # Adjust segment and shot counts
        nSeg = nSeg - 1
        if nShot_off > 0:
            y_raw[:, :, :, 1:nShot_off] = np.nan
        nShot = nShot - nShot_off

        # Remove ROOSK data (if roosk_flag is True)
        if roosk_flag:
            y_raw = y_raw[:, 1:2:end, :, :]

    N = N // 2
    y_raw = np.reshape(y_raw, [nCh, N, nSeg * nShot])

    # If nEcho == 2 (not implemented yet)
    if nEcho == 2:
        raise ValueError("bmTwix_data : nEcho == 2, case not implemented, yet. But we have to do it for Giulia's data ! ")

    # If none of the above conditions are met (also not implemented)
    else:
        raise ValueError("bmTwix_data : case not implemented. ")

    return y_raw
