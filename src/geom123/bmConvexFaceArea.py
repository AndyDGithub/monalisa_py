from __future__ import annotations
import numpy as np

def bmConvexFaceArea(x: np.ndarray, sort_on: bool) -> float:
    """Strict deterministic baseline port from MATLAB."""
    imDim = x.shape[0]
    nPt = x.shape[1]

    # If the dimension is 1, return 0 because there are no edges
    if imDim == 1:
        return 0.0
    elif imDim == 2:
        # Pad with zeros to make it 3D for consistency
        x = np.vstack((x, np.zeros_like(x[0])))

    # Calculate the centroid and vector difference from the centroid
    x0 = np.mean(x, axis=1)
    v = x - np.tile(x0, (nPt, 1))

    if sort_on:
        v1 = np.tile(v[:, 0], (nPt, 1))
        c = np.cross(v1, v)  # Direct cross product
        c_norm = np.sqrt(np.sum(c**2, axis=0))
        ind_max = np.argmax(c_norm)
        e3 = c[:, ind_max] / np.linalg.norm(c[:, ind_max])
        e1 = v[:, ind_max] / np.linalg.norm(v[:, ind_max])
        e1_rep = np.tile(e1, (nPt, 1))

        myCos = np.dot(e1.T, v)
        mySin = np.dot(e3.T, np.cross(e1_rep, v))
        myPhase = np.angle(myCos + 1j * mySin)
        myPerm = np.argsort(myPhase)
        v = v[:, myPerm]

    # Compute the cross product of adjacent vectors
    z = np.roll(v, -1, axis=1)
    out = np.linalg.norm(np.sum(np.cross(v, z), axis=0)) / 2

    return out
