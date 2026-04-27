"""Auto-generated from MATLAB source. Review manually before production use."""

from src.geom1.bmVolumeElement1 import bmVolumeElement1
from src.geom123.bmVoronoi import bmVoronoi
from src.traj123.bmTraj_lineDirection import bmTraj_lineDirection
from src.traj123.bmTraj_lineReshape import bmTraj_lineReshape
from third_part.matlab_compat.matlab_native import repmat

from src.sparseMat.m.bmSparseMat_vec import error
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# The strategy adopted here to deal with nonUnique lines is to perturbe
# randomly a little bit each line in order to separate them. The
# perturbation is inversely proportional to the magic_number
# perturbe_factor.

import numpy as np

def bmVolumeElement_voronoi_full_radial3_nonUnique(t):
    # check -------------------------------------------------------------------
    # TODO(matlab-control): if not(size(t, 1) == 3)
    error("This function is for 3D trajectory only. ")
    # TODO(matlab-line): return;
    # END_check ---------------------------------------------------------------
    t       = bmTraj_lineReshape(t)
    imDim   = np.shape(t, 1)
    N       = np.shape(t, 2)
    nLine   = np.shape(t, 3)
    e = bmTraj_lineDirection(t)
    # TODO(matlab-control): if (N/2 - fix(N/2)) > 0
    # TODO(matlab-line): error(['The number of points per line must be even, because the ', ...
    # TODO(matlab-line): '0 must be at index position N/2+1']);
    # TODO(matlab-line): return;
    # constructing dr ---------------------------------------------------------
    dr = np.zeros(N, nLine)
    # TODO(matlab-control): for i = 1:nLine
    # TODO(matlab-line): dr(:, i) = t(:, :, i)'*e(:, i);
    dr = bmVolumeElement1(dr);  # Here, the size(dr) must be [N, nLine]
    # END_constructing dr -----------------------------------------------------
    # constructing ds ---------------------------------------------------------
    ds = bmSphericalVoronoi_1_nonUnique(t, "half")
    ds = repmat(ds, [N, 1])
    # TODO(matlab-line): ds = ds.*squeeze(bmTraj_squaredNorm(t));
    # END_constructing ds -----------------------------------------------------
    # TODO(matlab-line): v = dr(:)'.*ds(:)';
    # center volume element ---------------------------------------------------
    # TODO(matlab-line): dr_0 = mean(dr(N/2+1, :), 2)/2;
    # TODO(matlab-line): v(1, N/2+1:N:end) = (4/3)*pi*(dr_0^3)/(2*nLine);
    # END_center volume element -----------------------------------------------
    return v

def bmSphericalVoronoi_1_nonUnique(t, half_or_full):
    perturbe_factor = 1000;  # ------------------------------------------------------- magic number
    imDim = np.shape(t, 1)
    N = np.shape(t, 2)
    nLine = np.shape(t, 3)
    # TODO(matlab-line): s = squeeze(t(:, end, :));
    s_norm = np.zeros(1, np.shape(s, 2))
    # TODO(matlab-control): for i = 1:imDim
    # TODO(matlab-line): s_norm = s_norm + s(i, :).^2;
    s_norm = sqrt(s_norm)
    s_norm_rep = repmat(s_norm, [np.shape(s, 1), 1])
    # TODO(matlab-line): s = s./s_norm_rep;
    # random_perturbation -----------------------------------------------------
    nPoint_s = np.shape(s, 2)
    dS = 0
    # TODO(matlab-control): if strcmp(half_or_full, 'half')
    dS = 2*pi/nPoint_s
    # TODO(matlab-control): elseif strcmp(half_or_full, 'full')
    dS = 4*pi/nPoint_s
    dL = sqrt(dS)/perturbe_factor
    # TODO(matlab-control): if (dL <= eps)
    error("The perturbation is too small")
    # TODO(matlab-line): return;
    myRand = 2*(np.random.rand(np.shape(s)) - 0.5)*dL
    s = s + myRand
    s_norm = np.zeros(1, np.shape(s, 2))
    # TODO(matlab-control): for i = 1:imDim
    # TODO(matlab-line): s_norm = s_norm + s(i, :).^2;
    s_norm = sqrt(s_norm)
    s_norm_rep = repmat(s_norm, [np.shape(s, 1), 1])
    # TODO(matlab-line): s = s./s_norm_rep;
    # END_random_perturbation -------------------------------------------------
    # TODO(matlab-control): if strcmp(half_or_full, 'half')
    s = cat(2, s, -s)
    # TODO(matlab-line): myIndex = 1:size(s, 2);
    # TODO(matlab-line): temp_mask = s(1, :) >= 0;
    # TODO(matlab-line): s_p1    = s(:, temp_mask);
    ind_p1  = myIndex(1, temp_mask)
    # TODO(matlab-line): temp_mask = s(1, :) <= 0;
    # TODO(matlab-line): s_m1    = s(:, temp_mask);
    ind_m1  = myIndex(1, temp_mask)
    # TODO(matlab-line): temp_mask = s(2, :) >= 0;
    # TODO(matlab-line): s_p2    = s(:, temp_mask);
    ind_p2  = myIndex(1, temp_mask)
    # TODO(matlab-line): temp_mask = s(2, :) <= 0;
    # TODO(matlab-line): s_m2    = s(:, temp_mask);
    ind_m2  = myIndex(1, temp_mask)
    # TODO(matlab-line): temp_mask = s(3, :) >= 0;
    # TODO(matlab-line): s_p3    = s(:, temp_mask);
    ind_p3  = myIndex(1, temp_mask)
    # TODO(matlab-line): temp_mask = s(3, :) <= 0;
    # TODO(matlab-line): s_m3    = s(:, temp_mask);
    ind_m3  = myIndex(1, temp_mask)
    # TODO(matlab-line): v_p1 = bmSphericalVoronoi_2(s_p1(3, :), s_p1(2, :),  s_p1(1, :));
    # TODO(matlab-line): v_m1 = bmSphericalVoronoi_2(s_m1(3, :), s_m1(2, :), -s_m1(1, :));
    # TODO(matlab-line): v_p2 = bmSphericalVoronoi_2(s_p2(3, :), s_p2(1, :),  s_p2(2, :));
    # TODO(matlab-line): v_m2 = bmSphericalVoronoi_2(s_m2(3, :), s_m2(1, :), -s_m2(2, :));
    # TODO(matlab-line): v_p3 = bmSphericalVoronoi_2(s_p3(1, :), s_p3(2, :),  s_p3(3, :));
    # TODO(matlab-line): v_m3 = bmSphericalVoronoi_2(s_m3(1, :), s_m3(2, :), -s_m3(3, :));
    v = np.zeros(6, np.shape(s, 2))
    # TODO(matlab-line): v(1, ind_p1) = v_p1;
    # TODO(matlab-line): v(2, ind_m1) = v_m1;
    # TODO(matlab-line): v(3, ind_p2) = v_p2;
    # TODO(matlab-line): v(4, ind_m2) = v_m2;
    # TODO(matlab-line): v(5, ind_p3) = v_p3;
    # TODO(matlab-line): v(6, ind_m3) = v_m3;
    # TODO(matlab-line): v = v(:, 1:nLine);
    myWeight = (v > 0)
    # TODO(matlab-line): v = sum(v, 1)./sum(myWeight, 1);
    return v

def bmSphericalVoronoi_2(s1, s2, s3):
    # TODO(matlab-line): s = cat(1, s1(:)', s2(:)', s3(:)');
    nPt = np.shape(s, 2)
    # TODO(matlab-line): myIndex = 1:nPt;
    myIndex = myIndex.ravel().T
    myAngle = acos(1/sqrt(3))
    myAngle = (pi/2 - myAngle)/3
    h1 = sin(1*myAngle)
    h2 = sin(2*myAngle)
    h3 = sin(3*myAngle)
    # TODO(matlab-line): myMask_1 = (s(3, :) < h1);
    # TODO(matlab-line): s(:, myMask_1) = [];
    # TODO(matlab-line): myIndex(:, myMask_1) = [];
    # TODO(matlab-line): myMask_2 = s(3, :) < h2;
    # TODO(matlab-line): p = s(1:2, :)./repmat(s(3, :), [2, 1]);
    myVoronoi = bmVoronoi(p)
    myVoronoi = myVoronoi.ravel().T
    # TODO(matlab-line): myVoronoi(1, myVoronoi <= 0) = 0;
    # TODO(matlab-line): myVoronoi(1, myMask_2) = 0;
    # TODO(matlab-line): myVoronoi = myVoronoi.*abs(s(3, :).^3);
    out = np.zeros(1, nPt)
    # TODO(matlab-line): out(1, myIndex) = myVoronoi;
    return out
