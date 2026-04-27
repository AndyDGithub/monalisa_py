from __future__ import annotations
from third_part.matlab_compat.matlab_native import size


def bmImReg_solidTransform_distance(T1, T2, half_imRadius):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: c1  = T1.c_ref;
    # MATLAB: c2  = T2.c_ref;
    # MATLAB: if norm(c1(:) - c2(:)) > 0
    # MATLAB: d = Inf;
    # MATLAB: return;
    # MATLAB: end
    # MATLAB: t1 = T1.t;
    # MATLAB: t2 = T2.t;
    # MATLAB: n = abs(half_imRadius);
    # MATLAB: imDim = size(t1(:), 1);
    # MATLAB: if imDim == 2
    # MATLAB: a1 = T1.R(:, 1)*n;
    # MATLAB: a2 = T2.R(:, 1)*n;
    # MATLAB: p1 = cat(1, t1(:), a1(:));
    # MATLAB: p2 = cat(1, t2(:), a2(:));
    # MATLAB: d = norm(p1(:) - p2(:))/2;
    # MATLAB: elseif imDim == 3
    # MATLAB: R1 = T1.R;
    # MATLAB: R2 = T2.R;
    # MATLAB: R = R1*inv(R2);
    # MATLAB: dR = norm(bmCol(  (R - eye(imDim))*n  ));
    # MATLAB: dt = norm(  t1(:) - t2(:)  );
    # MATLAB: d = sqrt(  (dR^2 + dt^2)/6  );
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    d = None
    return d
