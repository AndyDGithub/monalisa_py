import numpy as np

def bmTraj_resolution(t):
    """Compute the resolution in each dimension of a trajectory.

    MATLAB reference:
    % Bastien Milani
    % CHUV and UNIL
    % Lausanne - Switzerland
    % May 2023

    function varargout = bmTraj_resolution(t)

    imDim = size(t, 1);

    if imDim > 0
        x_max = max(t(1, :));
        x_min = min(t(1, :));
        dx = 1/abs(x_max - x_min); 
    end

    if imDim > 1
        y_max = max(t(2, :));
        y_min = min(t(2, :));
        dy = 1/abs(y_max - y_min); 
    end

    if imDim > 2
        z_max = max(t(3, :));
        z_min = min(t(3, :));
        dz = 1/abs(z_max - z_min); 
    end

    if imDim == 1
        varargout{1} = dx;
    elseif imDim == 2
        varargout{1} = [dx, dy];
    elseif imDim == 3
        varargout{1} = [dx, dy, dz];
    end
    """
    imDim = t.shape[0]

    dx = None
    dy = None
    dz = None

    if imDim > 0:
        x_max = np.max(t[0])
        x_min = np.min(t[0])
        dx = 1 / np.abs(x_max - x_min)

    if imDim > 1:
        y_max = np.max(t[1])
        y_min = np.min(t[1])
        dy = 1 / np.abs(y_max - y_min)

    if imDim > 2:
        z_max = np.max(t[2])
        z_min = np.min(t[2])
        dz = 1 / np.abs(z_max - z_min)

    if imDim == 1:
        return dx
    if imDim == 2:
        return [dx, dy]
    if imDim == 3:
        return [dx, dy, dz]
    # In case of unexpected dimension, return None
    return None
