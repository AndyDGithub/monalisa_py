import numpy as np
from scipy.spatial import Voronoi, ConvexHull
from src.geom1.bmVolumeElement1 import bmVolumeElement1


def bmVoronoi(x, varargin=None):
    x = np.array(x).astype(np.float64)
    imDim = x.shape[0]
    nPt = x.shape[1]
    out = np.zeros((1, nPt))
    disp_flag = True

    if varargin is not None:
        disp_flag = bool(varargin[0])

    if imDim == 1:
        return bmVolumeElement1(x)

    if imDim in [2, 3]:
        if disp_flag:
            print('Running "voronoin" and "convhulln"... can take some time ...')

        try:
            # 'Qbb' scales the bounding box; 'Qz' adds a point at infinity
            vor = Voronoi(x.T, qhull_options='Qbb Qc Qz')
        except Exception:
            out[:] = -1
            if disp_flag:
                print('... "voronoin" failed (degenerate input), all set to -1.')
            return out

        for j in range(nPt):
            region_idx = vor.point_region[j]
            region = vor.regions[region_idx]
            # -1 in region means a vertex at infinity (MATLAB index 1)
            if len(region) > 0 and -1 not in region:
                vertices = vor.vertices[region, :]
                try:
                    hull = ConvexHull(vertices)
                    out[0, j] = hull.volume
                except Exception:
                    out[0, j] = -1
            else:
                out[0, j] = -1

        if disp_flag:
            print('... "voronoin" and "convhulln" done !')

    return out
