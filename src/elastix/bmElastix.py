import numpy as np
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape from arrayUtility

def bmElastix(argImageList, nDim, argParamFile, argTempDir, **kwargs):
    myFixIndex = kwargs.get('FixIndex', 1)
    myMaskFlag = kwargs.get('Mask', None) is not None
    myClearFlag = kwargs.get('ClearTempDir', True)

    # Return images unchanged
    myImageList = np.copy(argImageList)

    if nDim == 2:
        deformation_shape = (*argImageList.shape[:2], 2, argImageList.shape[2])
    else:
        deformation_shape = (*argImageList.shape[:3], 3, argImageList.shape[3])

    myDeformFieldList = np.zeros(deformation_shape)
    myDeformParamFileList = [None] * argImageList.shape[nDim]

    return [myImageList, myDeformFieldList, myDeformParamFileList]
