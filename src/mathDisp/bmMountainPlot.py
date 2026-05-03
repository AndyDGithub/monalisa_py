import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def t(M, varargin):
    """Strict deterministic baseline port from MATLAB."""
    M = np.array(M, dtype=float)
    
    if len(varargin) > 1:
        x = np.array(varargin[0])
        y = np.array(varargin[1])
    else:
        iMax, jMax = M.shape
        x = np.arange(1, iMax + 1)
        y = np.arange(1, jMax + 1)

    X, Y = np.meshgrid(x, y)
    
    # Flatten the data for interpolation
    points = np.column_stack((x.ravel(), y.ravel()))
    values = M.ravel()
    
    # Interpolate on a regular grid for plotting
    Z = griddata(points, values, (X, Y), method='linear')
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    
    plt.show()

# Auto-generated entrypoint alias for import compatibility
bmMountainPlot = t
