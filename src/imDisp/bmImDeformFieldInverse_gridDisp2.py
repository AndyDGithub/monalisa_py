from __future__ import annotations
import numpy as np

from src.imReg.m.bmImReg_deformField_to_positionField import bmImReg_deformField_to_positionField
from src.image123.bmImGradient import bmImGradient

def bmImDeformFieldInverse_gridDisp2(v, n_u, cell_width, *varargin):
    """
    Display the inverse deformField by mean of a checkerBoared.

    Parameters
    ----------
    v : Any
        Deform field data.
    n_u : Any
        Image size.
    cell_width : Any
        Width of a cell of the checkerboard. It must be equal or larger to 
2.
    *varargin : Any
        Optional background image and other parameters.

    Returns
    -------
    None
    """
    nan_value = -1  # magic_number

    backGroundIm = bmVarargin(varargin)

    if cell_width < 2:
        cell_width = 2
    elif cell_width > min(n_u):
        cell_width = min(n_u)

    v = bmBlockReshape(v, n_u)
    v = bmImReg_deformField_to_positionField(v, n_u, [], [], [], True)

    vx = v[:, :, 0]
    vy = v[:, :, 1]

    X = np.arange(1, n_u[0, 1] + 1)
    Y = np.arange(1, n_u[0, 2] + 1)
    X, Y = np.meshgrid(X, Y)

    myIm_x = private_checkerboard_x(n_u, cell_width)
    myIm_x = interpn(X, Y, myIm_x, vx, vy, 'linear')

    myIm_y = private_checkerboard_y(n_u, cell_width)
    myIm_y = interpn(X, Y, myIm_y, vx, vy, 'linear')

    gx = bmImGradient(myIm_x)
    gy = bmImGradient(myIm_y)

    gx1 = gx[:, :, 0]
    gx2 = gx[:, :, 1]
    gy1 = gy[:, :, 0]
    gy2 = gy[:, :, 1]

    myIm = np.sqrt(gx1**2 + gx2**2)
    myIm[myIm < 0.3] = 0
    myIm = np.clip(myIm, 0, 0.5)
    m = (myIm > 0)

    myIm_r = 0 * myIm
    myIm_g = 2 * myIm
    myIm_b = 0 * myIm
    myIm_rgb = np.stack((myIm_r, myIm_g, myIm_b), axis=-1)

    if not np.array_equal(backGroundIm, []):
        backGroundIm = abs(backGroundIm)
        backGroundIm -= np.min(backGroundIm)
        backGroundIm /= np.max(backGroundIm)

        b_r = backGroundIm
        b_g = backGroundIm
        b_b = backGroundIm
        b_r[m] = 0
        b_g[m] = 0
        b_b[m] = 0

        b_rgb = np.stack((b_r, b_g, b_b), axis=-1)

        myIm_rgb += b_rgb

    plt.figure()
    plt.imshow(myIm_rgb)
    plt.axis('image')
    plt.show()


def private_checkerboard_x(n_u, cell_width):
    myOne = np.ones(cell_width)
    myZero = np.zeros(cell_width)
    myOneZero = np.concatenate((myOne, myZero))

    myColumn = []
    for i in range(1, int(np.ceil(n_u[0, 1] / (2 * cell_width))) + 1):
        myColumn = np.concatenate((myColumn, myOneZero))

    myIm_x = np.tile(myColumn[:n_u[0, 1]], (1, n_u[0, 2]))
    return myIm_x


def private_checkerboard_y(n_u, cell_width):
    myOne = np.ones(cell_width)
    myZero = np.zeros(cell_width)
    myOneZero = np.concatenate((myOne, myZero))

    myRow = []
    for i in range(1, int(np.ceil(n_u[0, 2] / (2 * cell_width))) + 1):
        myRow = np.concatenate((myRow, myOneZero))

    myIm_y = np.tile(myRow[:n_u[0, 2]], (n_u[0, 1], 1))
    return myIm_y
