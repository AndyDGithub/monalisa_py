import numpy as np
from src.fieldDisp3.bmFieldPlot3_image import bmFieldPlot3_image
from src.fieldDisp3.bmFieldPlot3_noImage import bmFieldPlot3_noImage

def t3(x, y, z, vx, vy, vz, argSize, autoScaleFlag, normMax, varargin):
    argSize = argSize.ravel().T
    autoScaleFlag = False if autoScaleFlag is None else autoScaleFlag
    normMax = np.inf if normMax is None else normMax
    argImage = [] if varargin is None else varargin[0]

    if x is None or y is None or z is None:
        x, y, z = np.meshgrid(np.arange(argSize[0]), np.arange(argSize[1]), np.arange(argSize[2]))

    if argImage is None:
        bmFieldPlot3_noImage(x, y, z, vx, vy, vz, argSize, autoScaleFlag, normMax)
    else:
        bmFieldPlot3_image(x, y, z, vx, vy, vz, autoScaleFlag, normMax, argImage)

def bmFieldPlot3(x, y, z, vx, vy, vz, argSize, autoScaleFlag=None, normMax=None, varargin=None):
    return t3(x, y, z, vx, vy, vz, argSize, autoScaleFlag, normMax, varargin)
