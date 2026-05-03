# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmTextFile2Cell(arg_file):
    """Strict deterministic baseline port from MATLAB."""
    with open(arg_file, "r") as fid:
        lines = fid.readlines()
    c = [line.rstrip("\n") for line in lines]
    return c
