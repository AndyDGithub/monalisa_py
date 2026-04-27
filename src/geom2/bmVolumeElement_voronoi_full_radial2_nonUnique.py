import numpy as np
from src.geom1.bmVolumeElement1 import bmVolumeElement1
from src.traj123.bmTraj_lineDirection import bmTraj_lineDirection
from src.traj123.bmTraj_lineReshape import bmTraj_lineReshape

def bmVolumeElement_voronoi_full_radial2_nonUnique(t, nAverage):
    if not isinstance(t, np.ndarray):
        raise ValueError("Input t must be a numpy array.")
    if t.shape[0] != 2:
        raise ValueError("The trajectory must be 2Dim")

    t = bmTraj_lineReshape(t)
    imDim, N, nLine = t.shape

    e = bmTraj_lineDirection(t)
    dr = np.einsum('ijk,ik->ij', t, e)   # dot along first dim
    dr = bmVolumeElement1(dr)

    ds = np.linalg.norm(t, axis=0)
    ds = np.tile(ds, (N, 1))

    v = (dr * ds).sum(axis=0)

    if nAverage > 1:
        nPt = N // nLine
        v = np.zeros((nAverage, nPt))

        for i in range(nAverage):
            perturbed_t = t + np.random.rand(*t.shape) * (1 / 100) * (np.pi / N)
            v[i, :] = bmVolumeElement_voronoi_full_radial2_nonUnique(perturbed_t, 0)[1]

        v = np.mean(v, axis=0)

    return v
