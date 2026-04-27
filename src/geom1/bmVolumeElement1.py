import numpy as np


def bmVolumeElement1(x):
    x = np.asarray(x, dtype=np.float64)

    if x.ndim == 1 or x.shape[0] == 1 or x.shape[1] == 1:
        x = x.ravel()[:, np.newaxis]

    myPerm = np.argsort(x[:, 0])
    myInvPerm = np.argsort(myPerm)
    mySort = x[myPerm, :]

    myMid = (mySort[1:, :] + mySort[:-1, :]) / 2  # [N-1, nLine]

    first_row = mySort[0:1, :] - (myMid[0:1, :] - mySort[0:1, :])
    last_row = mySort[-1:, :] + (mySort[-1:, :] - myMid[-1:, :])
    myMid = np.concatenate([first_row, myMid, last_row], axis=0)  # [N+1, nLine]

    myDiff = myMid[1:, :] - myMid[:-1, :]  # [N, nLine]

    out = myDiff[myInvPerm, :]
    return out
