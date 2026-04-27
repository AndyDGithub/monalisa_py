import numpy as np

def bmTraj_resolution(t):
    imDim = np.shape(t, 1)

    if imDim > 0:
        x_max = np.max(t[0])
        x_min = np.min(t[0])
        dx = 1 / np.abs(x_max - x_min)
    else:
        dx = None

    if imDim > 1:
        y_max = np.max(t[1])
        y_min = np.min(t[1])
        dy = 1 / np.abs(y_max - y_min)
    else:
        dy = None

    if imDim > 2:
        z_max = np.max(t[2])
        z_min = np.min(t[2])
        dz = 1 / np.abs(z_max - z_min)
    else:
        dz = None

    varargout = [dx, dy, dz] if imDim > 0 else dx

    return varargout
