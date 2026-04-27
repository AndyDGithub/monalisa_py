import numpy as np
import matplotlib.pyplot as plt

def bmVarargin(args):
    # parse arguments
    return (None, False)

class bmImageViewerParam:
    def __init__(self, *args):
        self.point_list = np.empty((0,0))
        self.imSize = None
        self.mirror_flag = False
        self.reverse_flag = False
        self.transpose_flag = False
        self.colorLimits = (0, 1)
        self.point_A = None
        self.point_B = None
        self.point_C = None

def soft_coord(coord):
    return coord

def bmImage2(argImagesTable, *args):
    argParam, uiwait_flag = bmVarargin(args)
    if argParam is None:
        myParam = bmImageViewerParam()
    else:
        myParam = bmImageViewerParam(argParam)
    # convert logical to single if needed
    if isinstance(argImagesTable, np.ndarray) and argImagesTable.dtype == bool:
        argImagesTable = argImagesTable.astype(np.float32)
    myImagesTable = argImagesTable
    point_list = myParam.point_list
    imSize = myParam.imSize
    controlFlag = False
    shiftFlag = False
    escFlag = False
    # For simplicity skip GUI
    # Return myParam
    return myParam
