from __future__ import annotations

import numpy as np

from src.imDisp.bmImageViewerParam import bmImageViewerParam


def bmImage3(argImagesTable: np.ndarray, argParam=None, uiwait_flag: bool = False):
    """Interactive 3D image viewer (MATLAB GUI port).

    Authors:
        Bastien Milani
        CHUV and UNIL
        Lausanne - Switzerland
        May 2023

    Contributors:
        Dominik Helbing (Documentation, Comments, Help and Bug fixing)
        MattechLab 2024

    Parameters
    ----------
    argImagesTable : np.ndarray
        3-D array to visualise.
    argParam : bmImageViewerParam, optional
        Viewer parameters.  A default object is created from the data if
        not supplied.
    uiwait_flag : bool, optional
        When ``True`` the call should block until the figure is closed.

    Returns
    -------
    bmImageViewerParam
        The viewer parameters object (useful for retrieving placed points).
    """
    raise NotImplementedError(
        "bmImage3 requires a matplotlib-based interactive viewer. "
        "Planned for future implementation."
    )
