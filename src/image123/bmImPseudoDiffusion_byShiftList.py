from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty, single, size


def bmImPseudoDiffusion_byShiftList(argIm, argShiftList, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # initial
    # convolution
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: nIter = [];
    # MATLAB: if ~isempty(varargin)
    # MATLAB: nIter = varargin{1};
    # MATLAB: end
    # MATLAB: if isempty(nIter)
    # MATLAB: nIter = 1;
    # MATLAB: end
    # MATLAB: argIm = single(squeeze(argIm));
    # MATLAB: myDim = bmNdim(argIm);
    # MATLAB: if myDim == 1
    # MATLAB: argIm   = argIm(:);
    # MATLAB: end
    # MATLAB: argSize = size(argIm); argSize = argSize(:)';
    # MATLAB: out_1 = argIm;
    # MATLAB: nShift = size(argShiftList, 1);
    # MATLAB: for i = 1:nIter
    # MATLAB: myZeroMask = (out_1 == 0);
    # MATLAB: myZeroMask = reshape(myZeroMask, argSize);
    # MATLAB: myNonZeroMask = not(myZeroMask);
    # MATLAB: out_2 = zeros(argSize, 'single');
    # MATLAB: myNumOfNonZero = zeros(argSize, 'single');
    # MATLAB: for j = 1:nShift
    # MATLAB: out_2 = out_2 + circshift(out_1, argShiftList(j, :));
    # MATLAB: myNumOfNonZero = myNumOfNonZero + single(circshift(myNonZeroMask, argShiftList(j, :)));
    # MATLAB: end
    # MATLAB: myNumOfNonZero(myNumOfNonZero == 0) = 1;
    # MATLAB: out_1 = out_2./myNumOfNonZero;
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out_1 = None
    return out_1
