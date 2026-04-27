from src.arrayUtility.bmPointReshape import bmPointReshape
from src.traj123.bmTraj_squaredNorm import bmTraj_squaredNorm
import numpy as np

def bmVolumeElement_cartesian2(t):
    if not (len(np.shape(t)) == 2 or len(np.shape(t)) == 3 and t.shape[0] == 2):
        raise ValueError('The trajectory must be 2Dim')

    t = bmPointReshape(t)
    imDim = np.shape(t, 1)
    nPt = np.shape(t, 2)

    myDiff = np.repeat(t[:, 0], nPt).reshape((nPt, imDim)) - t
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    myMaxInd = np.argmax(mySquareNorm, axis=1)
    c1 = t[np.arange(imDim), myMaxInd]

    myDiff = np.repeat(c1, nPt).reshape((nPt, imDim)) - t
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    myMaxInd = np.argmax(mySquareNorm, axis=1)
    c2 = t[np.arange(imDim), myMaxInd]

    p_c1 = t - np.repeat(c1, nPt).reshape((nPt, imDim))
    e = (c2 - c1) / np.linalg.norm(c2 - c1)
    s = np.sum(e * p_c1, axis=0).reshape((imDim, 1))
    s = np.repeat(s, nPt, axis=0)

    myDiff = p_c1 - s * np.repeat(e, nPt).reshape((nPt, imDim))
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    myMaxInd = np.argmax(mySquareNorm, axis=1)
    c3 = t[np.arange(imDim), myMaxInd]

    myDiff = np.repeat(c3, nPt).reshape((nPt, imDim)) - t
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    myMaxInd = np.argmax(mySquareNorm, axis=1)
    c4 = t[np.arange(imDim), myMaxInd]

    l3 = np.linalg.norm(c3 - c1, axis=0)
    b3 = (c3 - c1) / l3
    l4 = np.linalg.norm(c4 - c1, axis=0)
    b4 = (c4 - c1) / l4

    R = np.linalg.inv([b3.ravel(), b4.ravel()])
    t = np.dot(R, t)

    dK_1 = np.sort(t[0, :])
    dK_2 = np.diff(dK_1)[np.where(np.abs(np.diff(dK_1)) > np.max(np.abs(dK_1))/3)]
    dK_2 = np.mean(dK_2)

    dK_1 = np.sort(t[1, :])
    dK_3 = np.diff(dK_1)[np.where(np.abs(np.diff(dK_1)) > np.max(np.abs(dK_1))/3)]
    dK_3 = np.mean(dK_3)

    v = dK_2 * dK_3 * np.ones((imDim, nPt))

    return v
