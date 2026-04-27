from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.image123.bmImGrid import bmImGrid
from src.varargin.bmVarargin import bmVarargin
from src.imReg.m.bmImReg_deformField_to_positionField import bmImReg_deformField_to_positionField
import numpy as np

def bmImReg_deform(v, x, n_u, X, Y, Z, varargin):
    [interp_method, circular_option] = bmVarargin(varargin)
    interp_method = "cubic" if not interp_method else interp_method
    circular_option = True if not circular_option else circular_option

    imDim = np.shape(n_u.ravel(), 1)
    [X, Y, Z] = bmImGrid(n_u, X, Y, Z)
    x = bmBlockReshape(x, n_u)
    v = bmImReg_deformField_to_positionField(v, n_u, X, Y, Z, circular_option)
    v = bmBlockReshape(v, n_u)

    if imDim == 2:
        x_deform = np.interp(X.ravel(), X.flatten(), np.interp(Y.ravel(), Y.flatten(), np.interp(x.ravel(), Z.flatten(), v[:, :, 1], method=interp_method), method=interp_method))
    elif imDim == 3:
        x_deform = np.interp(X.ravel(), X.flatten(), np.interp(Y.ravel(), Y.flatten(), np.interp(Z.ravel(), Z.flatten(), v[:, :, :, 1], method=interp_method), method=interp_method))
        x_deform = np.interp(x.ravel(), Z.flatten(), x_deform, method=interp_method)

    x_deform[np.isnan(x_deform)] = 0
    return x_deform
