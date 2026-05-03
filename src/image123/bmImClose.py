"""Auto-generated from MATLAB source. Review manually before production use
use."""

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.image123.bmImDilate import bmImDilate
from src.image123.bmImErode import bmImErode

def bmImClose(argIm, argShiftList):
    """
    Perform morphological closing on an image using dilation followed by er
erosion.

    Parameters:
        argIm (numpy.ndarray): Input image.
        argShiftList: Shift list for the morphological operations.

    Returns:
        numpy.ndarray: Closed image after dilation and erosion.
    """
    out = argIm
    out = bmImDilate(out, argShiftList)
    out = bmImErode(out, argShiftList)
    return out
