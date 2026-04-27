from third_part.twix_for_monalisa.mapVBVD_JH_for_monalisa import mapVBVD_JH_for_monalisa
import numpy as np

def bmTwix(argFile):
    myTwix = mapVBVD_JH_for_monalisa(argFile)
    if isinstance(myTwix, list):
        myTwix = myTwix[-1]
    return myTwix
