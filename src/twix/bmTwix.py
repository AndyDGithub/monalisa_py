from third_part.twix_for_monalisa.mapVBVD_JH_for_monalisa import mapVBVD_JH_for_monalisa
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Import bmBlockReshape to resolve ModuleNotFoundError

def bmTwix(argFile):
    # Extracts the Twix object as a struct from a Siemens raw data file

    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023

    # Parameters:
    # argFile (str): A string with the path to the data file

    # Returns:
    # myTwix (dict): A dictionary containing the extracted Twix object

    myTwix = mapVBVD_JH_for_monalisa(argFile)

    if isinstance(myTwix, list):  # Use isinstance instead of iscell for Python
        myTwix = myTwix[-1]

    return myTwix
