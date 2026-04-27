from src.arrayUtility.bmColReshape import bmColReshape
from src.image123.bmImGrid import bmImGrid
import numpy as np

def bmImReg_transform_to_deformField(argTransform, n_u, X, Y, Z):
    imDim = np.shape(n_u.ravel(), 1)
    n_u = n_u.ravel().T
    [X, Y, Z] = bmImGrid(n_u, X, Y, Z)

    if argTransform.class_type == 'bmImReg_translationTransform':
        t = argTransform.t.ravel()

        if imDim == 2:
            vx = np.ones(n_u)*t[0]
            vy = np.ones(n_u)*t[1]
            v = np.concatenate((vx, vy), axis=0)

        elif imDim == 3:
            vx = np.ones(n_u)*t[0]
            vy = np.ones(n_u)*t[1]
            vz = np.ones(n_u)*t[2]
            v = np.concatenate((vx, vy, vz), axis=0)

    elif argTransform.class_type == 'bmImReg_solidTransform':
        [X, Y, Z] = bmImGrid(n_u, X, Y, Z)

        t       = argTransform.t.ravel()
        c_ref   = argTransform.c_ref.ravel()
        R       = argTransform.R

        if imDim == 2:
            r = np.concatenate((X.ravel(), Y.ravel()), axis=0)
            r = r - np.tile(c_ref, (1, prod(n_u.ravel())))
            v = R @ r - r + np.tile(t, (1, prod(n_u.ravel())))
            v = np.concatenate((v[0], v[1]), axis=0)

        elif imDim == 3:
            r = np.concatenate((X.ravel(), Y.ravel(), Z.ravel()), axis=0)
            r = r - np.tile(c_ref, (1, prod(n_u.ravel())))
            v = R @ r - r + np.tile(t, (1, prod(n_u.ravel())))
            v = np.concatenate((v[0], v[1], v[2]), axis=0)

    elif argTransform.class_type == 'bmImReg_directTransform':
        v = bmColReshape(argTransform.v, n_u)

    return v
