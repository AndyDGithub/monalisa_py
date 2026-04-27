import numpy as np
from src.image123.bmImGrid import bmImGrid  # Assuming the existence of this function in the 'src/image123' module
from src.imReg import bmImReg_solidTransform, bmImReg_getInitialTranslationTransform_estimate_2, \

from src.imReg.m.bmImReg_getInitialSolidTransform_estimate import bmImReg_getInitialSolidTransform_estimate
    bmImReg_getCenterMass_estimate, bmImReg_transform_to_deformField, bmImReg_deform  # Assuming the existence of these functions in 'src/imReg' module
from src.mask123.bmElipsoidMask import bmElipsoidMask

def bmImReg_getInitialSolidTransform_recursive(imRef, imMov, nIter_max, initialTranslationTransform=None):
    halfPixLength = 0.5

    n_u = np.shape(imRef)
    n_u = n_u.ravel().T
    imDim = np.shape(n_u.ravel(), 1)
    X, Y, Z = bmImGrid(n_u, X=None, Y=None, Z=None)

    mySolidTransform = bmImReg_solidTransform()
    temp_solidTransform = bmImReg_solidTransform()

    if initialTranslationTransform is not None:
        mySolidTransform.t = initialTranslationTransform.t
    else:
        if imDim == 2:
            myTrans = bmImReg_getInitialTranslationTransform_estimate_2(imRef, imMov, X, Y, Z)
            mySolidTransform.t = myTrans.t
        elif imDim == 3:
            mySolidTransform.t = np.zeros([imDim, 1], "single")

    mySolidTransform.c_ref = bmImReg_getCenterMass_estimate(imRef, X, Y, Z)
    mySolidTransform.R = np.eye(imDim)

    imReg = imMov

    for i in range(nIter_max):
        temp_solidTransform = bmImReg_getInitialSolidTransform_estimate(imRef, imReg, X, Y, Z)

        mySolidTransform.t = mySolidTransform.R @ temp_solidTransform.t + mySolidTransform.t
        mySolidTransform.R = mySolidTransform.R @ temp_solidTransform.R

        v = bmImReg_transform_to_deformField(mySolidTransform, n_u, X, Y, Z)
        imReg = bmImReg_deform(v, imMov, n_u, X, Y, Z)

        R_rest = temp_solidTransform.R - np.eye(imDim)
        R_rest = np.sqrt((np.linalg.norm(R_rest)**2) / imDim)
        t_rest = np.linalg.norm(temp_solidTransform.t)

        if (t_rest < halfPixLength) and (R_rest < halfPixLength):
            break

    imReg = bmImReg_deform(v, imMov, n_u, X, Y, Z)
    m = bmElipsoidMask(n_u, n_u / 2)
    imReg = imReg * np.float64(m)

    return imReg
