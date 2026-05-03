import numpy as np

from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmIsBlockShape import bmIsBlockShape
from src.arrayUtility.bmIsColShape import bmIsColShape
from src.arrayUtility.bmBlockReshape import bmBlockReshape

def bmRMS(x, N_u):
    """Compute the root mean square (RMS) value for each data point across 

all channels.

    Parameters
    ----------
    x : ndarray
        The data for which the RMS should be calculated.
    N_u : list or tuple
        The size of the data of one channel in `x`.

    Returns
    -------
    a : ndarray
        The RMS for every data point in either block or column format depen
depen
depending on the
        format of `x` (block or other).
    """
    # Reshape data to column format
    c = bmColReshape(x, N_u)

    # Calculate RMS for each data point across the channels (rows)
    a = np.squeeze(np.sqrt(np.mean(np.abs(c)**2, axis=1)))

    # Reshape RMS data into block or column format, depending on x
    if bmIsColShape(x, N_u):
        a = bmColReshape(a, N_u)
    elif bmIsBlockShape(x, N_u):
        a = bmBlockReshape(a, N_u)

    return a
