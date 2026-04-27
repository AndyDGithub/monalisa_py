"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmPointReshape import bmPointReshape
from src.traj123.bmTraj_squaredNorm import bmTraj_squaredNorm
from third_part.matlab_compat.matlab_native import repmat

from src.sparseMat.m.bmSparseMat_vec import error
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmVolumeElement_cartesian3(t):
    t = bmPointReshape(t)
    imDim = np.shape(t, 1)
    nPt = np.shape(t, 2)
    # TODO(matlab-control): if not(imDim == 3)
    error("The trajectory must be 3Dim")
    # TODO(matlab-line): return;
    # TODO(matlab-line): myDiff = repmat(t(:, 1), [1, nPt]) - t;
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    # TODO(matlab-line): [~, myMaxInd] = max(mySquareNorm);
    # TODO(matlab-line): c1 = t(:, myMaxInd);
    myDiff = repmat(c1, [1, nPt]) - t
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    # TODO(matlab-line): [~, myMaxInd] = max(mySquareNorm);
    # TODO(matlab-line): c2 = t(:, myMaxInd);
    p_c1 = t - repmat(c1, [1, nPt])
    e = (c2 - c1)/norm(c2 - c1)
    s = e.T*p_c1
    s = repmat(s, [imDim, 1])
    # TODO(matlab-line): myDiff = p_c1 - s.*repmat(e, [1, nPt]);
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    # TODO(matlab-line): [~, myMaxInd] = max(mySquareNorm);
    # TODO(matlab-line): c3 = t(:, myMaxInd);
    myDiff = repmat(c3, [1, nPt]) - t
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    # TODO(matlab-line): [~, myMaxInd] = max(mySquareNorm);
    # TODO(matlab-line): c4 = t(:, myMaxInd);
    p_c1 = t - repmat(c1, [1, nPt])
    e = (c3 - c1)/norm(c3 - c1)
    s = e.T*p_c1
    s = repmat(s, [imDim, 1])
    # TODO(matlab-line): myDiff = p_c1 - s.*repmat(e, [1, nPt]);
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    # TODO(matlab-line): [~, myMaxInd] = max(mySquareNorm);
    # TODO(matlab-line): c5_temp3 = t(:, myMaxInd);
    p_c1 = t - repmat(c1, [1, nPt])
    e = (c4 - c1)/norm(c4 - c1)
    s = e.T*p_c1
    s = repmat(s, [imDim, 1])
    # TODO(matlab-line): myDiff = p_c1 - s.*repmat(e, [1, nPt]);
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    # TODO(matlab-line): [~, myMaxInd] = max(mySquareNorm);
    # TODO(matlab-line): c5_temp4 = t(:, myMaxInd);
    e3 = (c3-c1)/norm(c3-c1)
    e4 = (c4-c1)/norm(c4-c1)
    n = cross(e3, e4)
    d3 = np.abs(n.T*(c5_temp3 - c1))
    d4 = np.abs(n.T*(c5_temp4 - c1))
    # TODO(matlab-control): if d3 < d4
    c5 = c5_temp4
    l1 = norm(c3 - c1)
    l2 = norm(c5 - c3)
    b1 = (c3 - c1)/l1
    b2 = (c5 - c3)/l2
    # TODO(matlab-control): else
    c5 = c5_temp3
    l1 = norm(c4 - c1)
    l2 = norm(c5 - c4)
    b1 = (c4 - c1)/l1
    b2 = (c5 - c4)/l2
    myDiff = repmat(c5, [1, nPt]) - t
    mySquareNorm = bmTraj_squaredNorm(myDiff)
    # TODO(matlab-line): [~, myMaxInd] = max(mySquareNorm);
    # TODO(matlab-line): c6 = t(:, myMaxInd);
    l3 = norm(c6 - c1)
    b3 = (c6 - c1)/l3
    R = inv([b1.ravel(), b2.ravel(), b3.ravel()])
    t = R*t
    # TODO(matlab-line): dK = sort(t(1, :));
    # TODO(matlab-line): dK = dK(1, 2:end) - dK(1, 1:end-1);
    dK_th = max(dK.ravel())/3
    dK_mask = (dK > dK_th)
    dK_1 = np.mean(dK(dK_mask.ravel()))
    # TODO(matlab-line): dK = sort(t(2, :));
    # TODO(matlab-line): dK = dK(1, 2:end) - dK(1, 1:end-1);
    dK_th = max(dK.ravel())/3
    dK_mask = (dK > dK_th)
    dK_2 = np.mean(dK(dK_mask.ravel()))
    # TODO(matlab-line): dK = sort(t(3, :));
    # TODO(matlab-line): dK = dK(1, 2:end) - dK(1, 1:end-1);
    dK_th = max(dK.ravel())/3
    dK_mask = (dK > dK_th)
    dK_3 = np.mean(dK(dK_mask.ravel()))
    v = dK_1*dK_2*dK_3*np.ones(1, nPt)
    return v
