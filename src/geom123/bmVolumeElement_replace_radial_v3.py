from __future__ import annotations
import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape

def bmVolumeElement_replace_radial_v3(x, v):
    nIter_max        = 6
    th_n1            = 3.5
    th_n_de          = 1.0 / 1000.0
    myEps            = 10.0 * np.finfo(float).eps
    delta_separation = myEps / (th_n_de / 1000.0)

    x   = np.asarray(bmPointReshape(x), dtype=float)
    out = np.asarray(v, dtype=float).ravel().copy()
    imDim, nPt = x.shape

    prob = ~np.isfinite(out) | (out <= 0)
    out[prob] = -1.0

    myRadius = np.sqrt(np.sum(x ** 2, axis=0))
    myRadius_max  = np.max(myRadius)
    myRadius_min  = np.min(myRadius)
    myRadius_half = (myRadius_max + myRadius_min) / 2.0
    isRadius_L = myRadius >= myRadius_half

    # d1: prepend zero column
    d1 = np.concatenate([np.zeros((imDim, 1)), x[:, 1:] - x[:, :-1]], axis=1)
    n1 = np.sqrt(np.sum(d1 ** 2, axis=0))
    n1[0] = 0.0

    median_n1 = np.median(n1[n1 > 0]) if np.any(n1 > 0) else 1.0
    isJumpLeft  = (n1 > th_n1 * median_n1)
    isJumpRight = np.roll(isJumpLeft, -1)
    isJumpLeft  = isJumpLeft  & isRadius_L
    isJumpRight = isJumpRight & isRadius_L

    nonSeparated_mask = n1 <= delta_separation
    n1_safe = n1.copy()
    n1_safe[nonSeparated_mask] = 1.0
    d1_safe = d1.copy()
    d1_safe[:, nonSeparated_mask] = 0.0
    nonSeparated_mask = nonSeparated_mask | np.roll(nonSeparated_mask, -1)

    e = d1_safe / np.maximum(n1_safe, myEps)
    de = np.concatenate([e[:, 1:] - e[:, :-1], np.zeros((imDim, 1))], axis=1)
    de[:, 0] = 0.0
    n_de = np.sqrt(np.sum(de ** 2, axis=0))
    dirChange_mask = n_de > th_n_de

    outOfLine_mask = isJumpLeft | isJumpRight | dirChange_mask | nonSeparated_mask
    myProblemMask  = outOfLine_mask & isRadius_L

    if isRadius_L[0]:
        myProblemMask[0] = True
    if isRadius_L[-1]:
        myProblemMask[-1] = True
    if np.linalg.norm(x[:, 0]) < myEps and out[0] > 0:
        myProblemMask[0] = False

    out[myProblemMask] = -1.0

    myRightRadius = np.roll(myRadius, -1)
    myLeftRadius  = np.roll(myRadius,  1)

    nIter  = 1
    myMask = out == -1.0
    while np.any(myMask) and nIter <= nIter_max:
        myRightVolume = np.roll(out, -1)[myMask]
        myLeftVolume  = np.roll(out,  1)[myMask]
        isRL  = myRadius[myMask]       >= myRadius_half
        isRS  = ~isRL
        isRRL = myRightRadius[myMask]  >= myRadius_half
        isRRS = ~isRRL
        isLRL = myLeftRadius[myMask]   >= myRadius_half
        isLRS = ~isLRL
        isJR  = isJumpRight[myMask]
        isJL  = isJumpLeft[myMask]

        myLeftAccept  = ((isRS & isLRS) | (isRL & isLRL)) & (myLeftVolume  > 0) & ~isJL
        myRightAccept = ((isRS & isRRS) | (isRL & isRRL)) & (myRightVolume > 0) & ~isJR

        weightAccept = myLeftAccept.astype(float) + myRightAccept.astype(float)
        zeroMask     = weightAccept == 0
        weightAccept[zeroMask] = 1.0

        myReplaceVolume = (myLeftVolume * myLeftAccept + myRightVolume * myRightAccept) / weightAccept
        myReplaceVolume[zeroMask] = -1.0

        out[myMask] = myReplaceVolume
        myMask = out < 0
        out[myMask] = -1.0
        nIter += 1

    prob = ~np.isfinite(out) | (out <= 0)
    if np.any(prob):
        raise ValueError('bmVolumeElement_replace_radial_v3: some problematic volume elements could not be replaced.')

    return out
