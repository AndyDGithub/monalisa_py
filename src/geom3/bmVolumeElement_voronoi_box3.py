import numpy as np

from src.arrayUtility.bmPointReshape import bmPointReshape
from src.geom3.bmVolumeElement_voronoi_center_out_radial3 import bmVoronoi

def bmVolumeElement_voronoi_box3(t, N_u, d_u):
    N_u = np.array(N_u).ravel().T
    d_u = np.array(d_u).ravel().T
    t   = bmPointReshape(t)
    nPt = np.shape(t, 2)

    Nx = int(N_u[0]) + 1
    Ny = int(N_u[1]) + 1
    Nz = int(N_u[2]) + 1

    x           = -(Nx/2)*d_u[0]
    y           = np.arange(-Ny/2, Ny/2-1) * d_u[1]
    z           = np.arange(-Nz/2, Nz/2-1) * d_u[2]

    [x_grid, y_grid, z_grid] = np.meshgrid(x, y, z)

    p1          = np.column_stack((x_grid.ravel(), y_grid.ravel(), z_grid.ravel()))
    # ... Continue generating and concatenating points p2 to p6 similarly

    t = np.concatenate([t, p1, p2, p3, p4, p5, p6], axis=0)

    ve = bmVoronoi(t)
    ve = ve[:, :nPt]

    return ve
