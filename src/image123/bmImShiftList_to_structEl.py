import numpy as np
from scipy import ndimage
from src.image123.bmImShiftList_to_image import bmImShiftList_to_image

def bmImShiftList_to_structEl(argShiftList):
    myStructEl = ndimage.minimum_filter(bmImShiftList_to_image(argShiftList), size=1) != 0
    if not np.array_equal(argShiftList, np.unique(myStructEl)):
        raise ValueError("There was a problem converting imShiftList to structEl.")
    return myStructEl
