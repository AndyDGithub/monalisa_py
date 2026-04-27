"""Auto-generated from MATLAB source. Review manually before production use."""

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.image123.bmImShiftList_to_structEl import bmImShiftList_to_structEl

def bmImErode(argIm, argShiftList):
    out = imerode(argIm, bmImShiftList_to_structEl(argShiftList))
    return out
