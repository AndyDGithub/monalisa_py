"""Auto-generated from MATLAB source. Review manually before production use."""

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.mathOp.bmEuclideProd import bmEuclideProd

def bmSquaredNorm(x, H):
    out = bmEuclideProd(x, x, H)
    return out
