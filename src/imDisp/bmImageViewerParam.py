"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmCol import bmCol
from src.varargin.bmVarargin import bmVarargin
# bmImageViewerParam < handle
# 
# This class only has properties and a constructor to fill the
# properties. This class contains the parameters used to create and
# manage an interactive figure that visualizes data as an image.
# 
# Authors:
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# 
# Contributors:
# Dominik Helbing (Documentation)
# MattechLab 2024
# 
# Constructor Parameters:
# argIn: Either an object of this class to create a copy, or an
# integer from 2 to 5 defining the dimension of the image.
# varargin{1}: The image data that should be displayed by a figure
# with these parameters. Required if argIn is only an integer.
# constructor *****************************************************

import numpy as np

def bmImageViewerParam(argIn, varargin):
    argIm           = bmVarargin(varargin)
    obj.imSize      = bmCol(np.shape(argIm)).T
    # TODO(matlab-control): if isa(argIn, 'bmImageViewerParam')
    obj.imDim               = argIn.imDim
    obj.imSize              = argIn.imSize
    obj.permutation         = argIn.permutation
    obj.transpose_flag      = argIn.transpose_flag
    obj.psi                 = argIn.psi
    obj.theta               = argIn.theta
    obj.phi                 = argIn.phi
    obj.point_A             = argIn.point_A
    obj.point_B             = argIn.point_B
    obj.point_C             = argIn.point_C
    obj.rotation            = argIn.rotation
    obj.reverse_flag        = argIn.reverse_flag
    obj.mirror_flag         = argIn.mirror_flag
    obj.numOfImages         = argIn.numOfImages
    obj.curImNum            = argIn.curImNum
    obj.colorLimits         = argIn.colorLimits
    obj.colorLimits_0       = argIn.colorLimits_0
    obj.numOfImages_4       = argIn.numOfImages_4
    obj.curImNum_4          = argIn.curImNum_4
    obj.numOfImages_5       = argIn.numOfImages_5
    obj.curImNum_5          = argIn.curImNum_5
    obj.point_list          = argIn.point_list
    # TODO(matlab-control): else
    obj.imDim               = np.shape(obj.imSize.ravel(), 1)
    obj.permutation         = []
    obj.psi                 = []
    obj.theta               = []
    obj.phi                 = []
    obj.point_A             = []
    obj.point_B             = []
    obj.point_C             = []
    obj.rotation            = []
    obj.transpose_flag      = False
    obj.reverse_flag        = False
    obj.mirror_flag         = False
    obj.numOfImages         = []
    obj.curImNum            = []
    # TODO(matlab-control): if (  min(argIm(:)  ) < max(  argIm(:)  )  )
    obj.colorLimits = [  min(argIm.ravel()), max(argIm.ravel())  ]
    # TODO(matlab-control): else
    obj.colorLimits = [0, 1]
    obj.colorLimits_0 = obj.colorLimits
    obj.numOfImages_4       = []
    obj.curImNum_4          = []
    obj.numOfImages_5       = []
    obj.curImNum_5          = []
    obj.point_list          = []
    # TODO(matlab-control): if argIn == 2
    obj.psi                 = 0
    obj.rotation            = eye(2)
    # TODO(matlab-control): elseif argIn == 3
    obj.permutation         = [1, 2, 3]
    obj.psi                 = 0
    obj.theta               = 0
    obj.phi                 = 0
    obj.rotation            = eye(3)
    obj.numOfImages         = obj.imSize(1, 3)
    obj.curImNum            = max(1, fix(  obj.numOfImages/2  ))
    # TODO(matlab-control): elseif argIn == 4
    # TODO(matlab-line): obj.imSize              = obj.imSize(1, 1:3);
    obj.permutation         = [1, 2, 3]
    obj.psi                 = 0
    obj.theta               = 0
    obj.phi                 = 0
    obj.rotation            = eye(3)
    obj.numOfImages         = obj.imSize(1, 3)
    obj.curImNum            = max(1, fix(  obj.numOfImages/2  ))
    obj.numOfImages_4       = np.shape(argIm, 4)
    obj.curImNum_4          = 1
    obj.point_list          = cell(obj.numOfImages_4, 1)
    # TODO(matlab-control): elseif argIn == 5
    # TODO(matlab-line): obj.imSize              = obj.imSize(1, 1:3);
    obj.permutation         = [1, 2, 3]
    obj.psi                 = 0
    obj.theta               = 0
    obj.phi                 = 0
    obj.rotation            = eye(3)
    obj.numOfImages         = obj.imSize(1, 3)
    obj.curImNum            = max(1, fix(  obj.numOfImages/2  ))
    obj.numOfImages_4       = np.shape(argIm, 4)
    obj.curImNum_4          = 1
    obj.numOfImages_5       = np.shape(argIm, 5)
    obj.curImNum_5          = 1
    obj.point_list          = cell(obj.numOfImages_4, obj.numOfImages_5)
    # END_constructor *************************************************
    end  # END method
    end  # END class
    return obj
