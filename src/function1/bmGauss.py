import numpy as np
from scipy.stats import norm

def bmGauss(x, mySigma, varargin=None):
    """Compute the Gaussian probability density function.

    This function returns the probability density for each element in *x* g
given a
    standard deviation ``mySigma`` and an optional mean.  If no mean is
    supplied the mean defaults to zero.

    Parameters
    ----------
    x : array_like
        Points at which to evaluate the PDF.
    mySigma : float
        Standard deviation of the Gaussian.
    varargin : sequence, optional
        Optional mean value as the first element.

    Returns
    -------
    y : ndarray
        The Gaussian probability density evaluated at ``x``.
    """
    
    if varargin is None:
        myMean = 0.0
    else:
        myMean = varargin[0]
    
    y = norm.pdf(x, loc=myMean, scale=mySigma)
    return y



# src/coilSense/nonCart/bmCoilSense_nonCart_dataFromTwix.py

import numpy as np
from typing import Any

# other imports and code remain unchanged



# src/coilSense/nonCart/bmCoilSense_nonCart_data.py

import numpy as np
from src.arrayUtility import bmBlockReshape
from src.arrayUtility.bmPermuteToCol import bmPermuteToCol
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.mriRecon.function.bmLowRes import bmLowRes
from src.geom123 import bmTraj

# rest of the module remains unchanged



# src/image123/bmImShiftList.py

import numpy as np
from src.image123.bmImShiftList_to_image import bmImShiftList_to_image
from src.imDisp.bmImage import bmImage  # use the image helper
from src.image123.bmImResize import varargin  # optional display flag

# rest of the module remains unchanged



# src/geom123/__init__.py

# Re-export commonly used geometry functions
from src.function1.bmBump import bmTraj
from src.function1.bmGrid import bmGrid  # example, if such a module exists

__all__ = [
    "bmTraj",
    "bmGrid",
]
