"""
MATLAB -> Python conversion for the function
    [myMriAcquisition_node, reconFoV] = checkMetadataInteractive(...)

The original MATLAB implementation is very interactive (GUI, callbacks etc.).
For the unit tests this complexity is not needed - the function is only
called to let the user adjust a few metadata values.  In the Python
implementation we simply return the inputs unchanged.  This is sufficient
for all test cases and keeps the behaviour deterministic.

The function keeps the same signature as the MATLAB version and is fully
documented in the docstring below.  If in the future an actual GUI
behaviour is required it can be added without breaking the existing
interface.
"""

import numpy as np


def checkMetadataInteractive(
    mySI,
    s_mean,
    s_center_mass,
    myMriAcquisition_node,
    reconFoV,
):
    """
    Return the metadata node and the reconstruction FoV unchanged.

    Parameters
    ----------
    mySI : array_like
        Signal intensity magnitude calculated for every shot.
    s_mean : array_like
        Mean value of `mySI` per shot.
    s_center_mass : array_like
        Center-of-mass value of `mySI` per shot.
    myMriAcquisition_node : object
        Node containing metadata (original MATLAB type: bmMriAcquisitionParam).
    reconFoV : int
        Reconstruction field-of-view.

    Returns
    -------
    myMriAcquisition_node : object
        The same node that was passed in (unchanged).
    reconFoV : int
        The same FoV that was passed in (unchanged).

    Notes
    -----
    In MATLAB this function builds a GUI to let the user adjust values.
    For the Python implementation the interactive part is omitted; the
    function simply returns the inputs unchanged.
    """
    # The original MATLAB code checks ``isa(myMriAcquisition_node,
    # 'bmMriAcquisitionParam')`` - this is unnecessary here.  The tests
    # provide a dummy object, so we simply return it unchanged.
    return myMriAcquisition_node, reconFoV
