from src.arrayUtility.bmColReshape import bmColReshape
import numpy as np

def bmGut_partialCartesian(y, ind_u, N_u):
    """
    Convert a partially Cartesian dataset to a full dataset.

    Parameters
    ----------
    y : np.ndarray
        Partially Cartesian dataset.
    ind_u : np.ndarray
        Indices of the non-zero elements.
    N_u : np.ndarray
        Number of points in each dimension.

    Returns
    -------
    x : np.ndarray
        Full dataset.
    """
    # Ensure inputs are double precision
    N_u = np.array(N_u, dtype=np.double).ravel()
    ind_u = np.array(ind_u, dtype=np.double).ravel()

    nCh = y.shape[1]
    nPt = y.size // nCh

    y = bmColReshape(y, nPt)
    
    x_shape = np.prod(N_u), nCh
    x = np.zeros(x_shape, dtype="single")
    if not np.isrealobj(y):
        x = complex(x, x)

    for i in range(nCh):
        x[ind_u, i] = y[:, i]

    return x
