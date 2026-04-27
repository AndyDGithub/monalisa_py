from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.imReg.m.bmImReg_deformField_to_positionField import bmImReg_deformField_to_positionField
from third_part.matlab_compat.matlab_native import double, logical
import numpy as np
from src.imDisp.bmImage import bmImage


def private_checkerboard(n_u, cell_width):
    myOne       = np.ones(cell_width)
    myZero      = np.zeros(cell_width)
    myOneZero   = np.concatenate((myOne, myZero))

    myColumn = []
    for i in range(1, int(np.ceil(n_u[0] / (2 * cell_width))) + 1):
        myColumn = np.concatenate((myColumn, myOneZero))

    myColumn_1 = myColumn[:n_u[0]]
    myColumn_2 = double(~logical(myColumn_1))

    myBlock_1 = []
    myBlock_2 = []
    for i in range(cell_width):
        myBlock_1.append(myColumn_1)
        myBlock_2.append(myColumn_2)

    myBlock = np.concatenate((myBlock_1, myBlock_2), axis=0)

    myIm = []
    for i in range(1, int(np.ceil(n_u[1] / (2 * cell_width))) + 1):
        myIm = np.concatenate((myIm, myBlock))

    return myIm


def p2(v, n_u, cell_width):
    if cell_width < 2:
        cell_width = 2
    elif cell_width > min(n_u):
        cell_width = min(n_u)

    v = bmBlockReshape(v, n_u)
    v = bmImReg_deformField_to_positionField(v, n_u, [], [], [], False)

    vx = v[:, :, 0]
    vy = v[:, :, 1]

    myIm = private_checkerboard(n_u, cell_width)
    [X, Y] = np.meshgrid(np.arange(1, n_u[0]+1), np.arange(1, n_u[1]+1))
    myIm = np.interp2d(X, Y, myIm, (vx, vy), method='linear')

    myIm[np.isnan(myIm)] = 0
    bmImage(myIm)


def bmImDeformFieldInverse_checkerboardDisp2(v, n_u, cell_width):
    p2(v, n_u, cell_width)
