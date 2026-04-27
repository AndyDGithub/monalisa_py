import numpy as np
from src.arrayUtility import bmBlockReshape  # Assuming this module exists or will be created

def bmVarargin_sparseType(sparseType):
    """Auto-generated from MATLAB source. Review manually before production use."""

    # This function returns the default sparse type if sparseType is empty.
    #
    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    #
    # Parameters;
    # sparseType (str): String containing the sparse type, default value is 'bmSparseMat'.
    #
    # Returns:
    # out (str): Contains given sparse type or default value if empty.
    # Return sparseType if given, return bmSparseMat if empty.

    out = "bmSparseMat"
    if sparseType:
        out = sparseType

    return out
