import numpy as np
from third_part.matlab_compat.matlab_native import permute

def bmTwix_data(myTwix, myMriAcquisition_node):
    # y_raw = bmTwix_data(myTwix, myMriAcquisition_node)
    #
    # Returns raw MRI data from a Twix object based on acquisition parameters.
    #
    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    #
    # Contributors:
    # Dominik Helbing (Documentation)
    # MattechLab 2024
    #
    # Parameters:
    # myTwix (struct): Struct containing Twix MRI data.
    # myMriAcquisition_node (struct): Struct containing acquisition
    # parameters.
    #
    # Returns:
    # y_raw (array): Raw MRI data in the [nCh, N, nLine] shape, where nLine
    # is nShot * nSeg, which can change depending on the selfNav_flag and
    # nShot_off in myMriAcquisition_node.
    #
    # Notes:
    # This function reshapes and processes the raw data based on the
    # acquisition parameters such as the number of segments, shots,
    # channels, and echoes. It also handles optional flags for self
    # navigation and ROOSK.
    #
    # Example:
    # y_raw = bmTwix_data(myTwix, myMriAcquisition_node);

    N               = myMriAcquisition_node.N
    nSeg            = myMriAcquisition_node.nSeg
    nShot           = myMriAcquisition_node.nShot
    nCh             = myMriAcquisition_node.nCh
    nEcho           = myMriAcquisition_node.nEcho
    selfNav_flag    = myMriAcquisition_node.selfNav_flag
    nShot_off       = myMriAcquisition_node.nShot_off
    roosk_flag      = myMriAcquisition_node.roosk_flag

    # unsorted() returns the unsorted data as an array [N, nCh, nSeg*nShot]
    y_raw   = myTwix.image.unsorted()

    # Change structure to [nCh, N, nLine] and seperate nLine into nSeg and nShot
    y_raw   = permute(y_raw, [2, 1, 3])
    y_raw   = np.reshape(y_raw, [nCh, N, nSeg, nShot])

    # If a navigation was acquired it should be removed from the rawdata
    # (remove first segment)
    if selfNav_flag:
        nSeg = nSeg - 1
        y_raw = np.delete(y_raw, 0, axis=2)

    # Remove all shots that were not in steady state
    if nShot_off > 0:
        nShot = nShot - nShot_off
        y_raw = np.delete(y_raw, range(nShot_off), axis=3)

    # ask Bastien?
    if roosk_flag:
        y_raw = y_raw[:, :, ::2, :]
        N = N // 2

    # Reshape the output to [nCh, N, nSeg*nShot]
    y_raw  = np.reshape(y_raw, [nCh, N, nSeg * nShot])

    if nEcho == 2:
        raise ValueError("bmTwix_data : nEcho == 2, case not implemented, yet. But we have to do it for Giulia's data ! ")
    else:
        raise ValueError("bmTwix_data : case not implemented. ")

    return y_raw
