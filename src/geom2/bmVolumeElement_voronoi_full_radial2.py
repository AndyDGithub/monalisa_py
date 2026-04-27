import numpy as np
from src.geom2 import bmTraj_lineReshape, bmVolumeElement1, bmTraj_lineDirection, bmVoronoi
from src.traj123.bmTraj_norm import bmTraj_norm
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Import bmBlockReshape

def bmVolumeElement_voronoi_full_radial2(t):
    if t.shape[0] != 2:
        raise ValueError("The trajectory must be 2Dim")
        return None

    t = bmTraj_lineReshape(t)
    imDim = np.shape(t, 1)
    N = np.shape(t, 2)
    nLine = np.shape(t, 3)
    e = bmTraj_lineDirection(t)

    # Construct dr
    dr = np.zeros((N, nLine))
    for i in range(nLine):
        dr[:, i] = t[:, :, i].T @ e[:, i]
    dr = bmVolumeElement1(dr)  # Here, the size(dr) must be [N, nLine]

    # Construct ds
    ee = np.concatenate((e, -e), axis=1)
    myAngle = np.angle(complex(ee[0], ee[1]))
    myPerm = np.argsort(myAngle)
    myInvPerm = np.argsort(myPerm)

    myCutSpace = (np.pi - myAngle[-1, 0]) + (myAngle[0, 0] - (-np.pi))
    myVoronoi_1 = (myAngle[1, 1] - myAngle[1, 0]) / 2 + myCutSpace / 2
    myVoronoi_end = (myAngle[-1, -1] - myAngle[-1, -2]) / 2 + myCutSpace / 2

    myAngleVoronoi = bmVoronoi(myAngle.ravel())
    myAngleVoronoi = myAngleVoronoi.reshape(-1, nLine)

    myAngleVoronoi[0, 0] = myVoronoi_1
    myAngleVoronoi[-1, -1] = myVoronoi_end

    myAngleVoronoi = myAngleVoronoi[:, myInvPerm]
    ds = bmTraj_norm(t) * np.sin(myAngleVoronoi).reshape(-1, N)  # This is for 2DimRadial.

    v = dr.flatten() * ds.flatten()  # TODO: Implement the logic for handling even number of points per line

    # Center volume element
    dr_0 = np.mean(dr[N // 2, :], axis=1) / 2
    v0 = np.pi * (dr_0**2) / (2 * nLine)
    v[N // 2 + 1:N:end] = v0

    return v
