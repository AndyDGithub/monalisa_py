"""Auto-generated from MATLAB source. Review manually before production use."""

from src.image123.bmImGrid import bmImGrid
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.imReg.m.bmImReg_getCenterMass_estimate import bmImReg_getCenterMass_estimate
import numpy as np

def bmImReg_getInitialTranslationTransform_estimate(imRef, imMov, X, Y, Z):
    n_u = np.shape(imRef)
    n_u = n_u.ravel().T
    imDim = np.shape(n_u.ravel(), 1)
    myTranslationTransform      = bmImReg_translationTransform
    [X, Y, Z] = bmImGrid(n_u, X, Y, Z)
    c_ref = bmImReg_getCenterMass_estimate(imRef, X, Y, Z)
    c_mov = bmImReg_getCenterMass_estimate(imMov, X, Y, Z)
    myTranslationTransform.t    = c_mov.ravel() - c_ref.ravel()
    return myTranslationTransform
