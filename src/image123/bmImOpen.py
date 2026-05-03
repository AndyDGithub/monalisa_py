"""Auto-generated from MATLAB source. Review manually before production use
use."""

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.image123.bmImDilate import bmImDilate
from src.image123.bmImErode import bmImErode

def bmImOpen(argIm, argShiftList):
    """
    Perform morphological opening on the input image using erosion followed
followed by dilation.

    Args:
        argIm (numpy.ndarray): Input image.
        argShiftList (list): List of shifts for morphological operations.

    Returns:
        numpy.ndarray: Output image after morphological opening.
    """
    out = argIm
    out = bmImErode(out, argShiftList)
    out = bmImDilate(out, argShiftList)
    return out
