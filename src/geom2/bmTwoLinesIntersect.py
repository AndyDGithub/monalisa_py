import numpy as np

def bmTwoLinesIntersect(ax, ay, bx, by, cx, cy, dx, dy):
    """Compute the intersection point of two lines defined by four points a
a, b, c, d."""
    a = np.array([ax, ay], dtype=float)
    b = np.array([bx, by], dtype=float)
    c = np.array([cx, cy], dtype=float)
    d = np.array([dx, dy], dtype=float)

    n = (b - a) / np.linalg.norm(b - a)
    m = (d - c) / np.linalg.norm(d - c)

    # Helper for 2-D cross product (scalar)
    def cross2d(u, v):
        return u[0] * v[1] - u[1] * v[0]

    denom = cross2d(n, m)
    if np.isclose(denom, 0):
        # Lines are parallel or coincident; return a point on the line
        return float('nan'), float('nan')

    t = cross2d(c - a, m) / denom
    o = a + t * n
    return o[0], o[1]
