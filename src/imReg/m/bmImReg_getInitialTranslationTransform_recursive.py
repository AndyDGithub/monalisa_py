from src.image123.bmImGrid import bmImGrid
from src.imReg.m.bmImReg_deform import bmImReg_deform
from src.imReg.m.bmImReg_getInitialTranslationTransform_estimate import bmImReg_getInitialTranslationTransform_estimate
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Imported to fix the ModuleNotFoundError
import numpy as np

from src.imReg.m.bmImReg_transform_to_deformField import bmImReg_transform_to_deformField

def bmImReg_getInitialTranslationTransform_recursive(imRef, imMov, nIter_max, X, Y, Z):
    halfPixLength = 1/2  # ------------------------------------------------------------ magic_number
    n_u = np.shape(imRef)
    n_u = n_u.ravel().T
    imDim = np.shape(n_u.ravel(), 1)
    [X, Y, Z] = bmImGrid(n_u, X, Y, Z)

    myTranslationTransform = bmImReg_translationTransform
    temp_translationTransform = bmImReg_translationTransform
    myTranslationTransform.t = np.zeros([imDim, 1], "single")
    imReg = imMov

    for i in range(nIter_max):
        temp_translationTransform = bmImReg_getInitialTranslationTransform_estimate(imRef, imReg, X, Y, Z)
        myTranslationTransform.t = temp_translationTransform.t + myTranslationTransform.t

        v = bmImReg_transform_to_deformField(myTranslationTransform, n_u)
        imReg = bmImReg_deform(v, imMov, n_u, X, Y, Z)

        if np.linalg.norm(temp_translationTransform.t) < halfPixLength:
            break

    return (v, myTranslationTransform, imReg)
