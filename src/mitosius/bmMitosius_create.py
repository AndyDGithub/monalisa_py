import os
import numpy as np
import scipy.io

from src.arrayUtility.bmIndex2MultiIndex import bmIndex2MultiIndex


def bmMitosius_create(mitosius_dir, *args):
    """
    Create a mitosius directory structure and optionally save y, t, ve data.

    Port of MATLAB bmMitosius_create.m.

    Signatures
    ----------
    bmMitosius_create(mitosius_dir, mitosius_length)
        Create empty directory structure for mitosius_length cells.

    bmMitosius_create(mitosius_dir, y_cell, t_cell, ve_cell)
        Save y/t/ve data for each cell.  y_cell, t_cell, ve_cell must be
        indexable (list, ndarray of objects, etc.) with length == number of cells.
    """
    y_cell          = None
    t_cell          = None
    ve_cell         = None
    mitosius_size   = None
    mitosius_length = None

    if len(args) == 1:
        mitosius_length = int(args[0])
        mitosius_size   = np.array([mitosius_length], dtype=np.float64)

    elif len(args) == 3:
        y_cell  = args[0]
        t_cell  = args[1]
        ve_cell = args[2]

        # Use len() for lists/sequences - np.shape on a list-of-arrays returns
        # the full array shape, not the cell shape.
        n = len(y_cell)
        mitosius_size   = np.array([n], dtype=np.float64)
        mitosius_length = n

    else:
        raise ValueError(
            "bmMitosius_create expects (dir, length) or (dir, y_cell, t_cell, ve_cell)."
        )

    os.makedirs(mitosius_dir, exist_ok=True)

    for i in range(1, mitosius_length + 1):
        multi_idx = bmIndex2MultiIndex(i, mitosius_size.astype(int))
        # MATLAB: num_id = '_1_1' (underscore before each index, 1-indexed)
        num_id = "".join(f"_{int(idx)}" for idx in multi_idx)
        cell_dir = os.path.join(mitosius_dir, f"cell{num_id}")
        os.makedirs(cell_dir, exist_ok=True)

        if y_cell is not None:
            y = y_cell[i - 1]
            scipy.io.savemat(os.path.join(cell_dir, "y.mat"), {"y": y})

        if t_cell is not None:
            t = t_cell[i - 1]
            scipy.io.savemat(os.path.join(cell_dir, "t.mat"), {"t": t})

        if ve_cell is not None:
            ve = ve_cell[i - 1]
            scipy.io.savemat(os.path.join(cell_dir, "ve.mat"), {"ve": ve})

    scipy.io.savemat(
        os.path.join(mitosius_dir, "mitosius_size.mat"),
        {"mitosius_size": mitosius_size},
    )
