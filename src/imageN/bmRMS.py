import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmIsBlockShape import bmIsBlockShape
from src.arrayUtility.bmIsColShape import bmIsColShape

def bmRMS(x, N_u):
    # Reshape data to column format
    c = bmColReshape(x, N_u)

    # Calculate RMS for each data point across the channels (rows)
    a = np.sqrt(np.mean(np.abs(c)**2, axis=1))

    # Reshape RMS data into block or column format, depending on x
    if bmIsColShape(x, N_u):
        a = np.reshape(a, (-1, 1) + tuple(N_u))
    elif bmIsBlockShape(x, N_u):
        a = bmBlockReshape(a, N_u)

    return a
