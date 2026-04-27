from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty, repmat, size


def bmVolumeElement_replace_radial_v3(x, v):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # This takes into account the presence of jumps if the ditance from the
    # origin is large enough. It takes also the non-separation and the change
    # of direction into account. The replacement is iterative.
    # 
    # Having a large radius is a necessary condition for a point to be added as
    # problematic.
    # 
    # This function is for k0- and nonk0- trajectories.
    # 
    # This is suitable for radial.
    # radius ------------------------------------------------------------------
    # END_radius --------------------------------------------------------------
    # jump_mask ---------------------------------------------------------------
    # END_jump_mask -----------------------------------------------------------
    # nonSeparated_mask -------------------------------------------------------
    # END_nonSeparated_mask ---------------------------------------------------
    # dirChangeMask -------------------------------------------------------
    # END_dirChangeMask -------------------------------------------------------
    # outOfLine_mask ----------------------------------------------------------
    # END_outOfLine_mask ------------------------------------------------------
    # adding problematic values -----------------------------------------------
    # END_adding problematic values -------------------------------------------
    # definition of shifted lists
    # we replace all the problematic volumes, the added and the others.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: x = bmPointReshape(x);
    # MATLAB: v = v(:)';
    # MATLAB: nIter_max = 6;   % ---------------------------------------------------------- magic number
    # MATLAB: th_n1 = 3.5; % -------------------------------------------------------------- magic number
    # MATLAB: th_n_de = 1/1000; % --------------------------------------------------------- magic number
    # MATLAB: myEps = 10*eps; % ----------------------------------------------------------- magic number
    # MATLAB: delta_separation = myEps/(th_n_de/1000); % ---------------------------------- magic number
    # MATLAB: imDim   = size(x, 1);
    # MATLAB: nPt     = size(x, 2);
    # MATLAB: out   = v;
    # MATLAB: myProblemMask = isnan(out) | isinf(out) | isempty(out) | not(isnumeric(out)) | (out <= 0);
    # MATLAB: out(myProblemMask) = -1;
    # MATLAB: myRadius = zeros(1, nPt);
    # MATLAB: for i = 1:imDim
    # MATLAB: myRadius = myRadius + x(i, :).^2;
    # MATLAB: end
    # MATLAB: myRadius        = sqrt(myRadius);
    # MATLAB: myRadius_max    = max(myRadius(:));
    # MATLAB: myRadius_min    = min(myRadius(:));
    # MATLAB: myRadius_half   = (myRadius_max + myRadius_min)/2;
    # MATLAB: isRadius_L      = (myRadius >= myRadius_half);
    # MATLAB: d1 = x(:, 2:nPt) - x(:, 1:nPt-1);
    # MATLAB: d1 = [zeros(imDim, 1), d1];
    # MATLAB: n1 = zeros(1, nPt);
    # MATLAB: for i = 1:imDim
    # MATLAB: n1 = n1 + d1(i, :).^2;
    # MATLAB: end
    # MATLAB: n1 = sqrt(n1);
    # MATLAB: n1(1, 1) = 0;
    # MATLAB: isJumpLeft    = ( n1(:)' > th_n1*median(n1(:)) );
    # MATLAB: isJumpRight   = circshift(isJumpLeft, [0, -1]);
    # MATLAB: isJumpLeft    = isJumpLeft  & isRadius_L;
    # MATLAB: isJumpRight   = isJumpRight & isRadius_L;
    # MATLAB: nonSeparated_mask = (n1 <= delta_separation);
    # MATLAB: n1(1, nonSeparated_mask) = 1;
    # MATLAB: for i =1:imDim
    # MATLAB: d1(i, nonSeparated_mask) = 0;
    # MATLAB: end
    # MATLAB: nonSeparated_mask = nonSeparated_mask | circshift(nonSeparated_mask, [0, -1]);
    # MATLAB: e  = d1./repmat(n1, [imDim, 1]);
    # MATLAB: de = e(:, 2:nPt) - e(:, 1:nPt-1);
    # MATLAB: de(:, 1) = zeros(imDim, 1);
    # MATLAB: de = [de, zeros(imDim, 1)];
    # MATLAB: n_de = zeros(1, nPt);
    # MATLAB: for i = 1:imDim
    # MATLAB: n_de = n_de + de(i, :).^2;
    # MATLAB: end
    # MATLAB: n_de = sqrt(n_de);
    # MATLAB: dirChange_mask = (n_de > th_n_de);
    # MATLAB: outOfLine_mask = (isJumpLeft | isJumpRight | dirChange_mask | nonSeparated_mask);
    # MATLAB: myProblemMask = outOfLine_mask & isRadius_L;
    # MATLAB: if isRadius_L(1, 1)
    # MATLAB: myProblemMask(1, 1) = true;
    # MATLAB: end
    # MATLAB: if isRadius_L(1, end)
    # MATLAB: myProblemMask(1, end) = true;
    # MATLAB: end
    # MATLAB: if (norm(x(:, 1)) < myEps) && (out(1, 1) > 0)
    # MATLAB: myProblemMask(1, 1) = false;
    # MATLAB: end
    # MATLAB: out(1, myProblemMask) = -1;
    # MATLAB: myMask = (out == -1);
    # MATLAB: myRightRadius   = circshift(myRadius, [0, -1]);
    # MATLAB: myLeftRadius    = circshift(myRadius, [0,  1]);
    # MATLAB: nIter = 1;
    # MATLAB: myMask = (out == -1);
    # MATLAB: while (sum(myMask(:)) > 0) && nIter <= nIter_max
    # MATLAB: myRightVolume   = circshift(out, [0, -1]);
    # MATLAB: myRightVolume   =  myRightVolume(myMask);
    # MATLAB: myLeftVolume    = circshift(out, [0,  1]);
    # MATLAB: myLeftVolume    =  myLeftVolume(myMask);
    # MATLAB: isRadius_L      = (myRadius(myMask) >= myRadius_half);
    # MATLAB: isRadius_S      = (myRadius(myMask) < myRadius_half);
    # MATLAB: isRightRadius_L = (myRightRadius(myMask) >= myRadius_half);
    # MATLAB: isRightRadius_S = (myRightRadius(myMask) < myRadius_half);
    # MATLAB: isLeftRadius_L  = (myLeftRadius( myMask) >= myRadius_half);
    # MATLAB: isLeftRadius_S  = (myLeftRadius( myMask) < myRadius_half);
    # MATLAB: isJumpRight_masked = isJumpRight(myMask);
    # MATLAB: isJumpLeft_masked  = isJumpLeft(myMask);
    # MATLAB: myLeftAccept  = (isRadius_S & isLeftRadius_S)  | (isRadius_L & isLeftRadius_L);
    # MATLAB: myLeftAccept  = myLeftAccept & (myLeftVolume > 0) & not(isJumpLeft_masked);
    # MATLAB: myRightAccept = (isRadius_S & isRightRadius_S) | (isRadius_L & isRightRadius_L);
    # MATLAB: myRightAccept = myRightAccept & (myRightVolume > 0) & not(isJumpRight_masked);
    # MATLAB: weightAccept = (myRightAccept + myLeftAccept);
    # MATLAB: zeroAcceptMask = (weightAccept == 0);
    # MATLAB: weightAccept(zeroAcceptMask) = 1;
    # MATLAB: myReplaceVolume = (myLeftVolume.*myLeftAccept + myRightVolume.*myRightAccept)./weightAccept;
    # MATLAB: myReplaceVolume(zeroAcceptMask) = -1;
    # MATLAB: out(myMask) = myReplaceVolume;
    # MATLAB: myMask = (out < 0);
    # MATLAB: out(myMask) = -1;
    # MATLAB: nIter = nIter + 1;
    # MATLAB: end
    # MATLAB: myProblemMask = isnan(out) | isinf(out) | isempty(out) | not(isnumeric(out)) | (out <= 0);
    # MATLAB: if sum(myProblemMask(:) > 0)
    # MATLAB: error('In bmVoronoi : some problematic volume elements could not be replaced. ');
    # MATLAB: out = [];
    # MATLAB: return;
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out = None
    return out
