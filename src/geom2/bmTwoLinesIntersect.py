from __future__ import annotations


def bmTwoLinesIntersect(ax, ay, bx, by, cx, cy, dx, dy):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: a = [ax, ay];
    # MATLAB: b = [bx, by];
    # MATLAB: c = [cx, cy];
    # MATLAB: d = [dx, dy];
    # MATLAB: n = (b-a)/norm(b-a);
    # MATLAB: m = (d-c)/norm(d-c);
    # MATLAB: p = a;
    # MATLAB: q = c;
    # MATLAB: r = p-q;
    # MATLAB: x = cross([n, 0], [m, 0]);
    # MATLAB: y = cross([m, 0], [r, 0]);
    # MATLAB: t_abs = norm(y)/norm(x);
    # MATLAB: if norm(y - t_abs*x) < norm(y)
    # MATLAB: t = t_abs;
    # MATLAB: else
    # MATLAB: t = -t_abs;
    # MATLAB: end
    # MATLAB: o = p + t*n;
    # MATLAB: ox = o(1);
    # MATLAB: oy = o(2);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    ox = None
    oy = None
    return ox, oy
