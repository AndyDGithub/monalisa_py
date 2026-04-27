import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmIsBlockShape import bmIsBlockShape
from src.arrayUtility.bmIsColShape import bmIsColShape


def bmMIP(y, N_u):
    # Reshape data to column format
    c = bmColReshape(y, N_u)
    # Calculate MIP of the data by taking the maximum across all channels for each data point
    a = np.max(np.abs(c), axis=2)
    # Reshape MIP data into block or column format, depending on x
    if bmIsColShape(y, N_u):
        a = bmColReshape(a, N_u)
    elif bmIsBlockShape(y, N_u):
        a = bmBlockReshape(a, N_u)

    return a
