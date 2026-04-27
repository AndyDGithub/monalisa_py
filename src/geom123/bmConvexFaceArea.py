from __future__ import annotations
from third_part.matlab_compat.matlab_native import repmat, size


def bmConvexFaceArea(x, sort_on):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # x must be of size [imDim, nPt], where imDim = 1 or 2 or 3.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: nPt = size(x, 2);
    # MATLAB: if size(x, 1) == 1
    # MATLAB: out = 0;
    # MATLAB: return;
    # MATLAB: elseif size(x, 1) == 2
    # MATLAB: x = cat(1, x, zeros(1, nPt));
    # MATLAB: end
    # MATLAB: x0      = mean(x, 2);
    # MATLAB: v       = x - repmat(x0, [1, nPt]);
    # MATLAB: if sort_on
    # MATLAB: v1      = repmat(v(:, 1), [1, nPt]);
    # MATLAB: c       = cross(v1, v);
    # MATLAB: c_norm = sqrt(c(1, :).^2 + c(2, :).^2 + c(3, :).^2);
    # MATLAB: [~, ind_max] = max(c_norm);
    # MATLAB: e3 = c(:, ind_max);         e3 = e3/norm(e3);
    # MATLAB: e1 = v(:, ind_max);         e1 = e1/norm(e1);
    # MATLAB: e1_rep = repmat(e1, [1, nPt]);
    # MATLAB: myCos = e1'*v;
    # MATLAB: mySin = e3'*cross(e1_rep, v);
    # MATLAB: myPhase = angle(complex(myCos, mySin));
    # MATLAB: [~, myPerm] = sort(myPhase);
    # MATLAB: v = v(:, myPerm);
    # MATLAB: end
    # MATLAB: z = circshift(v, [0, -1]);
    # MATLAB: out = norm(sum(cross(v, z), 2))/2;
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out = None
    return out
