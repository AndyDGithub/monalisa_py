from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty, size


def bmVolumeElement_replace_radial_v2(x, v):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # This take into account the distance from the origin and the presence of a
    # jump. The replacement is not iterative.
    # Having a large radius is a necessary condition for a point to be added as
    # problematic.
    # 
    # This function is for k0- and nonk0- trajectories.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: x = bmPointReshape(x);
    # MATLAB: v = v(:)';
    # MATLAB: th_factor = 1.5; % ----------------------------------------------------------- magic number
    # MATLAB: imDim = size(x, 1);
    # MATLAB: nPt   = size(x, 2);
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
    # MATLAB: myTrajDiff = x(:, 2:end) - x(:, 1:end-1);
    # MATLAB: myTrajJump = zeros(1, nPt - 1);
    # MATLAB: for i = 1:imDim
    # MATLAB: myTrajJump = myTrajJump + myTrajDiff(i, :).^2;
    # MATLAB: end
    # MATLAB: myTrajJump = sqrt(myTrajJump);
    # MATLAB: myTrajJump_th = median(myTrajJump)*th_factor;
    # MATLAB: myTrajJumpMask_left = (myTrajJump > myTrajJump_th);
    # MATLAB: myTrajJumpMask_left = [myTrajJumpMask_left, false];
    # MATLAB: myTrajJumpMask_right = circshift(myTrajJumpMask_left, [0, 1]);
    # MATLAB: myProblemMask = (myTrajJumpMask_left | myTrajJumpMask_right) & isRadius_L;
    # MATLAB: if isRadius_L(1, 1)
    # MATLAB: myProblemMask(1, 1) = true;
    # MATLAB: end
    # MATLAB: if isRadius_L(1, end)
    # MATLAB: myProblemMask(1, end) = true;
    # MATLAB: end
    # MATLAB: if (norm(x(:, 1)) < 10*eps) && (out(1, 1) > 0)
    # MATLAB: myProblemMask(1, 1) = false;
    # MATLAB: end
    # MATLAB: out(1, myProblemMask) = -1;
    # MATLAB: myMask = (out == -1);
    # MATLAB: isRadius_L      = (myRadius(myMask) >= myRadius_half);
    # MATLAB: isRadius_S      = (myRadius(myMask) < myRadius_half);
    # MATLAB: myRightRadius   = circshift(myRadius, [0, -1]);
    # MATLAB: isRightRadius_L = (myRightRadius(myMask) >= myRadius_half);
    # MATLAB: isRightRadius_S = (myRightRadius(myMask) < myRadius_half);
    # MATLAB: myLeftRadius    = circshift(myRadius, [0,  1]);
    # MATLAB: isLeftRadius_L  = (myLeftRadius( myMask) >= myRadius_half);
    # MATLAB: isLeftRadius_S  = (myLeftRadius( myMask) < myRadius_half);
    # MATLAB: myLeftVolume    = circshift(out, [0,  1]);
    # MATLAB: myLeftVolume    =  myLeftVolume(myMask);
    # MATLAB: myRightVolume   = circshift(out, [0, -1]);
    # MATLAB: myRightVolume   = myRightVolume(myMask);
    # MATLAB: myLeftAccept  = (isRadius_S & isLeftRadius_S)  | (isRadius_L & isLeftRadius_L);
    # MATLAB: myLeftAccept  = (myLeftAccept & (myLeftVolume > 0)  );
    # MATLAB: myRightAccept = (isRadius_S & isRightRadius_S) | (isRadius_L & isRightRadius_L);
    # MATLAB: myRightAccept = (myRightAccept & (myRightVolume > 0)  );
    # MATLAB: myProblemMask = myLeftAccept + myRightAccept;
    # MATLAB: myProblemMask = (myProblemMask == 0);
    # MATLAB: if sum(myProblemMask(:) > 0)
    # MATLAB: error('In bmVoronoi : some problematic volume elements could not be replaced. ');
    # MATLAB: out = [];
    # MATLAB: return;
    # MATLAB: end
    # MATLAB: myReplaceVolume = (myLeftVolume.*myLeftAccept + myRightVolume.*myRightAccept)./(myLeftAccept + myRightAccept);
    # MATLAB: out(myMask) = myReplaceVolume;
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
