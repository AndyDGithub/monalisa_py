from src.fieldDisp2.bmFieldPlot2_image import bmFieldPlot2_image
from src.fieldDisp2.bmFieldPlot2_noImage import bmFieldPlot2_noImage
import numpy as np
from src.arrayUtility.arrayUtility import bmBlockReshape  # Import missing module

def t2(x, y, vx, vy, argSize, autoScaleFlag, normMax, varargin):
    argSize = argSize.ravel().T
    autoScaleFlag = False if autoScaleFlag is None else autoScaleFlag
    normMax = np.inf if normMax is None else normMax
    argImage = []
    if varargin:
        argImage = varargin[0]
    [x, y] = np.meshgrid(x, y)
    if not argImage:
        bmFieldPlot2_noImage(x, y, vx, vy, argSize, autoScaleFlag, normMax)
    else:
        bmFieldPlot2_image(x, y, vx, vy, autoScaleFlag, normMax, argImage)

def bmFieldPlot2(x, y, vx, vy, argSize, autoScaleFlag=False, normMax=np.inf, varargin=[]):
    return t2(x, y, vx, vy, argSize, autoScaleFlag, normMax, varargin)
