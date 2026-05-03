from __future__ import annotations
import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape

def bmVolumeElement_replace_radial_v1(x, v):
    nIter_max   = 6
    th_factor_1 = 2.0
    th_factor_2 = 1.5

    x = np.asarray(bmPointReshape(x), dtype=float)
    out = np.asarray(v, dtype=float).ravel().copy()

    imDim, nPt = x.shape

    prob = ~np.isfinite(out) | (out <= 0)
    out[prob] = -1.0

    myRadius = np.sqrt(np.sum(x ** 2, axis=0))
    myRadius_max  = np.max(myRadius)
    myRadius_min  = np.min(myRadius)
    myRadius_half = (myRadius_max + myRadius_min) / 2.0
    isRadius_L = myRadius >= myRadius_half

    myTrajDiff = x[:, 1:] - x[:, :-1]
    myTrajJump = np.sqrt(np.sum(myTrajDiff ** 2, axis=0))
    myTrajJump_median = np.median(myTrajJump)

    myRadius_th  = myRadius_max - th_factor_1 * myTrajJump_median
    myRadiusMask = myRadius >= myRadius_th
    myProblemMask = myRadiusMask & isRadius_L

    if isRadius_L[0]:
        myProblemMask[0] = True
    if isRadius_L[-1]:
        myProblemMask[-1] = True
    out[myProblemMask] = -1.0

    myRightRadius = np.roll(myRadius, -1)
    myLeftRadius  = np.roll(myRadius,  1)

    myTrajJump_th = myTrajJump_median * th_factor_2
    isJumpRight_arr = np.concatenate([myTrajJump > myTrajJump_th, [True]])
    isJumpRight_arr = isJumpRight_arr & np.concatenate([isRadius_L[:-1], [isRadius_L[-1]]])
    isJumpLeft_arr  = np.roll(isJumpRight_arr, 1)

    nIter  = 1
    myMask = out == -1.0
    while np.any(myMask) and nIter <= nIter_max:
        myRightVolume = np.roll(out, -1)[myMask]
        myLeftVolume  = np.roll(out,  1)[myMask]
        isRL   = myRadius[myMask] >= myRadius_half
        isRS   = ~isRL
        isRRL  = myRightRadius[myMask] >= myRadius_half
        isRRS  = ~isRRL
        isLRL  = myLeftRadius[myMask]  >= myRadius_half
        isLRS  = ~isLRL
        isJR   = isJumpRight_arr[myMask]
        isJL   = isJumpLeft_arr[myMask]

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
        raise ValueError('bmVolumeElement_replace_radial_v1: some problematic volume elements could not be replaced.')

    return out
