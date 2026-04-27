from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.imReg.m.bmImReg_deformField_to_positionField import bmImReg_deformField_to_positionField
import matplotlib.pyplot as plt  # replace 'third_part.matlab_compat.matlab_native' with actual Python plotting library
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
# 
# 'v'               is the deformField.
# 'n_u'             is the image size.
# 'every_n_line'    is the number of lines we skip + 1, for the plot.
# (we don't want to plot every line, it is to much to
# plot).
# 
# 
# We work in image convention i.e. isotropic voxel_size with width equql 1
# in each dimension.


def p2(v, n_u, every_n_line):
    v = bmBlockReshape(v, n_u)
    v = bmImReg_deformField_to_positionField(v, n_u, [], [], [], False)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Plot grid lines
    ax.plot([1, 1], [1, n_u[0][1]], "g-", linewidth=2)
    ax.plot([1, n_u[0][2]], [1, 1], "g-", linewidth=2)
    ax.plot([n_u[0][2], n_u[0][2]], [1, n_u[0][1]], "g-", linewidth=2)
    ax.plot([1, n_u[0][2]], [n_u[0][1], n_u[0][1]], "g-", linewidth=2)

    # Plot displacement vectors
    for i in range(1, every_n_line + 1):
        x = v[:, i, 0]
        y = v[:, i, 1]
        ax.plot(y, x, 'b-')

    x_min = min(v[:, :, 0].ravel()) - n_u[0][1] / 20
    x_max = max(v[:, :, 0].ravel()) + n_u[0][1] / 20
    y_min = min(v[:, :, 1].ravel()) - n_u[0][2] / 20
    y_max = max(v[:, :, 1].ravel()) + n_u[0][2] / 20

    ax.plot(y_min, x_min, "k.")
    ax.plot(y_min, x_max, "k.")
    ax.plot(y_max, x_max, "k.")
    ax.plot(y_max, x_min, "k.")

    ax.set_box_aspect('equal')
    ax.invert_yaxis()

    return bmImDeformField_meshDisp2


def bmImDeformField_meshDisp2(v, n_u, every_n_line):
    return p2(v, n_u, every_n_line)
