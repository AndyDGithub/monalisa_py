from __future__ import annotations
import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape

def bmVolumeElement_replace_radial_v2(x, v):
    th_factor = 1.5

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

    myTrajDiff = x[:, 1:] - x[:, :-1]
    myTrajJump = np.sqrt(np.sum(myTrajDiff ** 2, axis=0))
    myTrajJump_th = np.median(myTrajJump) * th_factor

    myTrajJumpMask_left  = np.concatenate([myTrajJump > myTrajJump_th, [False]])
    myTrajJumpMask_right = np.roll(myTrajJumpMask_left, 1)

    myProblemMask = (myTrajJumpMask_left | myTrajJumpMask_right) & isRadius_L
    if isRadius_L[0]:
        myProblemMask[0] = True
    if isRadius_L[-1]:
        myProblemMask[-1] = True
    if np.linalg.norm(x[:, 0]) < 10 * np.finfo(float).eps and out[0] > 0:
        myProblemMask[0] = False

    out[myProblemMask] = -1.0

    myMask = out == -1.0
    isRL  = myRadius[myMask] >= myRadius_half
    isRS  = ~isRL

    myRightRadius = np.roll(myRadius, -1)
    isRRL = myRightRadius[myMask] >= myRadius_half
    isRRS = ~isRRL

    myLeftRadius = np.roll(myRadius, 1)
    isLRL = myLeftRadius[myMask] >= myRadius_half
    isLRS = ~isLRL

    myLeftVolume  = np.roll(out, 1)[myMask]
    myRightVolume = np.roll(out, -1)[myMask]

    myLeftAccept  = ((isRS & isLRS) | (isRL & isLRL)) & (myLeftVolume  > 0)
    myRightAccept = ((isRS & isRRS) | (isRL & isRRL)) & (myRightVolume > 0)

    weightAccept = myLeftAccept.astype(float) + myRightAccept.astype(float)
    cannotFix = weightAccept == 0
    if np.any(cannotFix):
        raise ValueError('bmVolumeElement_replace_radial_v2: some problematic volume elements could not be replaced.')

    myReplaceVolume = (myLeftVolume * myLeftAccept + myRightVolume * myRightAccept) / weightAccept
    out[myMask] = myReplaceVolume

    prob = ~np.isfinite(out) | (out <= 0)
    if np.any(prob):
        raise ValueError('bmVolumeElement_replace_radial_v2: some problematic volume elements could not be replaced.')

    return out
