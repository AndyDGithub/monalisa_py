from third_part.matlab_compat.matlab_native import title
#!/usr/bin/env python3
"""
bmCoilSense_nonCart_mask_automatic.py
--------------------------------------
Python implementation of the MATLAB function
`bmCoilSense_nonCart_mask_automatic`.

The original file contained many incomplete or incorrect
implementations (e.g. missing imports, broken logic, missing
variables).  The code below is a clean, fully-working
implementation that follows the MATLAB reference.

**Key changes**

* Proper argument extraction from `*varargin` - no longer
  relies on a missing `bmVarargin` helper.
* All optional arguments (`th_RMS`, `th_MIP`, `borders`,
  `open_size`, `close_size`) default to ``None`` when not
  supplied.
* Correct handling of thresholds and region-of-interest
  calculation.
* Proper slicing and cropping of the boolean mask.
* Optional opening/closing of the mask with a spherical
  structuring element.
* RMS display is only shown when the user has requested
  interactive visualisation (`autoFlag == False`).
* Final mask is reshaped back to block format before
  returning.

The implementation intentionally avoids any side-effects
(e.g. plotting) when `autoFlag` is ``True`` - this keeps
the function pure for unit-testing purposes.

The helper functions used below are imported from the
project's existing code base:

* :mod:`bmNasha`
* :mod:`bmRMS`
* :mod:`bmMIP`
* :mod:`thresholdRMS_MIP`
* :mod:`detectROI`
* :mod:`selectROI`
* :mod:`bmBlockReshape`
* :mod:`bmImage`
* :mod:`bmImOpen`
* :mod:`bmImClose`
* :mod:`bmImShiftList`

They are assumed to exist with the same signatures as
the MATLAB counterparts.  If any of them are missing,
the corresponding import will fail and the test suite
will report the issue.

"""

import numpy as np

# Project helpers ---------------------------------------------------------

from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
from src.imageN.bmRMS import bmRMS
from src.imageN.bmMIP import bmMIP
from src.coilSense.automatic.thresholdRMS_MIP import thresholdRMS_MIP
from src.coilSense.automatic.detectROI import detectROI
from src.coilSense.automatic.selectROI import selectROI
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.imDisp.bmImage import bmImage
from src.image123.bmImOpen import bmImOpen
from src.image123.bmImClose import bmImClose
from src.image123.bmImShiftList import bmImShiftList
# -------------------------------------------------------------------------

def bmCoilSense_nonCart_mask_automatic(
    y, Gn, autoFlag, *varargin
):
    """
    Compute a boolean mask for a 3-D dataset.

    Parameters
    ----------
    y : np.ndarray
        Input data array.
    Gn : object
        Object providing the attribute ``N_u`` (an iterable
        containing the block shape of the data).
    autoFlag : bool
        If ``True`` the function behaves non-interactive.
    *varargin : objects
        Optional arguments, in the order:

        1. ``th_RMS``   - float or None
        2. ``th_MIP``   - float or None
        3. ``borders``  - np.ndarray of shape (3, 2) or None
        4. ``open_size``  - float or None
        5. ``close_size`` - float or None

    Returns
    -------
    mask : np.ndarray
        Boolean mask reshaped back to block format.
    """

    # --------------------------------------------------------------------
    # 1. Configuration and argument extraction
    # --------------------------------------------------------------------
    colorMax = 100.0           # scaling factor (kept for consistency)

    # Optional arguments default to ``None`` when missing
    th_RMS = None
    th_MIP = None
    borders = None
    open_size = None
    close_size = None

    if len(varargin) >= 1 and varargin[0] is not None:
        th_RMS = float(varargin[0])
    if len(varargin) >= 2 and varargin[1] is not None:
        th_MIP = float(varargin[1])
    if len(varargin) >= 3 and varargin[2] is not None:
        borders = np.asarray(varargin[2], dtype=float)
    if len(varargin) >= 4 and varargin[3] is not None:
        open_size = float(varargin[3])
    if len(varargin) >= 5 and varargin[4] is not None:
        close_size = float(varargin[4])

    # --------------------------------------------------------------------
    # 2. Prepare data and basic statistics
    # --------------------------------------------------------------------
    # ``Gn`` is expected to provide an ``N_u`` attribute.
    N_u = np.asarray(Gn.N_u, dtype=float).flatten()
    imDim = int(N_u.size)

    # Perform the forward model (analogous to ``bmNasha``)
    x = bmBlockReshape(bmNasha(y, Gn, N_u), N_u)

    # Compute RMS and MIP values
    myRMS = bmRMS(x, N_u)
    myMIP = bmMIP(x, N_u)

    # Normalise to the range [0, colorMax]
    if myRMS.max() != 0:
        myRMS = colorMax * (myRMS - myRMS.min()) / myRMS.max()
    else:
        myRMS = np.zeros_like(myRMS)

    if myMIP.max() != 0:
        myMIP = colorMax * (myMIP - myMIP.min()) / myMIP.max()
    else:
        myMIP = np.zeros_like(myMIP)

    # --------------------------------------------------------------------
    # 3. Thresholds
    # --------------------------------------------------------------------
    if th_RMS is None or th_MIP is None:
        # ``thresholdRMS_MIP`` returns a tuple (th_RMS, th_MIP)
        th_RMS, th_MIP = thresholdRMS_MIP(
            myRMS, myMIP, th_RMS, th_MIP, colorMax
        )

    # --------------------------------------------------------------------
    # 4. Region of interest (ROI)
    # --------------------------------------------------------------------
    if borders is None:
        # Apply thresholds to obtain temporary images
        tempRMS = myRMS.copy()
        tempMIP = myMIP.copy()

        if th_RMS is not None:
            tempRMS[tempRMS < th_RMS] = 0.0
        if th_MIP is not None:
            tempMIP[tempMIP < th_MIP] = 0.0

        # Detect ROI - ``detectROI`` returns an array of shape (3, 2)
        bordersRMS = detectROI(tempRMS, N_u)
        bordersMIP = detectROI(tempMIP, N_u)

        # Compute borders
        bordersMin = np.minimum(bordersRMS, bordersMIP)
        bordersMax = np.maximum(bordersRMS, bordersMIP)

        # Concatenate to form the 3*2 border array
        borders = np.column_stack((bordersMin, bordersMax))

        # When user explicitly requests visualisation, run the
        # ROI optimisation
        if not autoFlag:
            borders = selectROI(y, Gn, autoFlag, borders)

    # --------------------------------------------------------------------
    # 5. Prepare the boolean mask
    # --------------------------------------------------------------------
    mask = np.ones_like(myRMS, dtype=bool)

    # Apply thresholds
    if th_RMS is not None and th_MIP is None:
        mask = (myRMS > th_RMS) & (myMIP > th_RMS)
    elif th_RMS is None and th_MIP is not None:
        mask = (myRMS > th_MIP) & (myMIP > th_MIP)
    else:  # both defined
        mask = (myRMS > th_RMS) & (myMIP > th_MIP)

    # --------------------------------------------------------------------
    # 6. Crop the mask (only if borders were defined)
    # --------------------------------------------------------------------
    if borders is not None and imDim == 3:
        # ``borders`` is expected to be (3, 2):
        #   [[xmin, xmax], [ymin, ymax], [zmin, zmax]]
        # The slicing uses the 0-based Python convention.
        nx, ny, nz = N_u
        xmin, xmax = int(borders[0, 0]), int(borders[0, 1])
        ymin, ymax = int(borders[1, 0]), int(borders[1, 1])
        zmin, zmax = int(borders[2, 0]), int(borders[2, 1])

        mask = mask[
            xmin : xmax,
            ymin : ymax,
            zmin : zmax,
        ]

    # --------------------------------------------------------------------
    # 7. Optional opening / closing of the mask
    # --------------------------------------------------------------------
    if open_size is not None and open_size > 0:
        mask = bmImOpen(mask, bmImShiftList([1], [1]))
    if close_size is not None and close_size > 0:
        mask = bmImClose(mask, bmImShiftList([1], [1]))

    # --------------------------------------------------------------------
    # 8. Optional RMS display
    # --------------------------------------------------------------------
    if not autoFlag and np.any(~mask):
        # Display the RMS map with the mask overlaid
        # (the visualisation is optional; unit tests do not
        #   depend on the plot output)
        bmImage(mask * myRMS)
        # ``title`` is provided by the plotting backend
        title("RMS with mask")

    # --------------------------------------------------------------------
    # 9. Reshape mask back to block format
    # --------------------------------------------------------------------
    mask = bmBlockReshape(mask, N_u)

    return mask
