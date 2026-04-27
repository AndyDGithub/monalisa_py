from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty, logical, single, size


def bmImConv_inMask_byShiftList(argIm, argShiftList, argMask, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # initial
    # numOfNonZero
    # convolution
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: nIter = [];
    # MATLAB: if ~isempty(varargin)
    # MATLAB: nIter = varargin{1};
    # MATLAB: end
    # MATLAB: if isempty(nIter)
    # MATLAB: nIter = 1;
    # MATLAB: end
    # MATLAB: argIm = single(argIm);
    # MATLAB: argMask = logical(argMask);
    # MATLAB: argSize = size(argIm);
    # MATLAB: argSize = argSize(:)';
    # MATLAB: myDim = bmNdim(argIm);
    # MATLAB: if myDim == 1
    # MATLAB: argSize = [max(argSize(:)), 1];
    # MATLAB: argIm   = argIm(:);
    # MATLAB: argMask = argMask(:);
    # MATLAB: end
    # MATLAB: myMask_neg = not(argMask);
    # MATLAB: out_1 = argIm;
    # MATLAB: out_1(myMask_neg) = 0;
    # MATLAB: out_2 = zeros(argSize, 'single');
    # MATLAB: nShift = size(argShiftList, 1);
    # MATLAB: myNumOfNonZero = zeros(argSize, 'single');
    # MATLAB: for i = 1:nShift
    # MATLAB: myNumOfNonZero = myNumOfNonZero + single(circshift(argMask, argShiftList(i, :)));
    # MATLAB: end
    # MATLAB: myNumOfNonZero(myMask_neg) = 1;
    # MATLAB: for i = 1:nIter
    # MATLAB: for j = 1:nShift
    # MATLAB: out_2 = out_2 + circshift(out_1, argShiftList(j, :));
    # MATLAB: end
    # MATLAB: out_1 = out_2./myNumOfNonZero;
    # MATLAB: out_1(myMask_neg) = 0;
    # MATLAB: out_2 = zeros(argSize, 'single');
    # MATLAB: end
    # MATLAB: out_1(myMask_neg) = argIm(myMask_neg);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out_1 = None
    return out_1
