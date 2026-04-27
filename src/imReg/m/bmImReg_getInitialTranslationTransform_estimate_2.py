from __future__ import annotations
from third_part.matlab_compat.matlab_native import size


def bmImReg_getInitialTranslationTransform_estimate_2(imRef, imMov, X, Y, Z):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: n_u = size(imRef);
    # MATLAB: n_u = n_u(:)';
    # MATLAB: imDim = size(n_u(:), 1);
    # MATLAB: myTranslationTransform      = bmImReg_translationTransform;
    # MATLAB: [~, ~, ~] = bmImGrid(n_u, X, Y, Z);
    # MATLAB: s = ones(1, imDim)*48; % ----------------------------------------------------- magic number
    # MATLAB: a = bmImResize(imRef, n_u, s);
    # MATLAB: b = bmImResize(imMov, n_u, s);
    # MATLAB: f = n_u./s;
    # MATLAB: r = zeros(s);
    # MATLAB: if imDim == 2
    # MATLAB: for i = 1:s(1, 1)
    # MATLAB: for j = 1:s(1, 2)
    # MATLAB: imShift = circshift(a, [i, j]);
    # MATLAB: r(i, j) = sum(abs(  imShift(:) - b(:)  ));
    # MATLAB: end
    # MATLAB: end
    # MATLAB: elseif imDim == 3
    # MATLAB: for i = 1:s(1, 1)
    # MATLAB: i;
    # MATLAB: for j = 1:s(1, 2)
    # MATLAB: for k = 1:s(1, 3)
    # MATLAB: imShift = circshift(a, [i, j, k]);
    # MATLAB: r(i, j, k) = sum(abs(  imShift(:) - b(:)  ));
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # MATLAB: [~, myInd] = min(r(:));
    # MATLAB: t = bmIndex2MultiIndex(myInd, s);
    # MATLAB: myTranslationTransform.t = t(:).*f(:);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    myTranslationTransform = None
    return myTranslationTransform
