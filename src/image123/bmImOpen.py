"""Auto-generated from MATLAB source. Review manually before production use."""

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.image123.bmImDilate import bmImDilate
from src.image123.bmImErode import bmImErode

def bmImOpen(argIm, argShiftList):
    out = argIm
    out = bmImErode(out , argShiftList)
    out = bmImDilate(out, argShiftList)
    return out
