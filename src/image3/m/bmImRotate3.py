from src.imReg.m.bmImReg_getCenterMass_estimate import bmImReg_getCenterMass_estimate
from src.image123.bmImGrid import bmImGrid
from src.linAlg3.bmRotation3_inv import bmRotation3_inv
from src.mask123.bmElipsoidMask import bmElipsoidMask
from src.varargin.bmVarargin import bmVarargin
from third_part.matlab_compat.matlab_native import repmat
import numpy as np


def bmImRotate3(arg_im, psi, theta, phi, varargin):
    c = bmVarargin(varargin)
    n_u = np.shape(arg_im)
    n_u = n_u.ravel().T
    imDim = np.shape(n_u.ravel(), 1)
    [X, Y, Z] = bmImGrid(n_u, [], [], [])

    m = bmElipsoidMask(n_u, n_u / 2)
    arg_im *= m

    c = bmImReg_getCenterMass_estimate(arg_im, X, Y, Z)
    c = c.ravel()

    R = bmRotation3_inv(psi, theta, phi)

    P = np.concatenate((X.flatten(), Y.flatten(), Z.flatten()), axis=0)
    P = P - repmat(c, [1, prod(n_u.ravel())])
    P = np.dot(R, P)
    P = P + repmat(c, [1, prod(n_u.ravel())])

    im_out = np.reshape(np.interp(P[0], X.flatten(), arg_im), n_u)
    im_out[np.isnan(im_out)] = 0
    im_out[np.isinf(im_out)] = 0

    return im_out
