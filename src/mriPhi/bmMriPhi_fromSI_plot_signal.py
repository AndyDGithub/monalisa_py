import numpy as np
from third_part.matlab_compat.matlab_native import plot

def bmMriPhi_fromSI_plot_signal(s, ind_shot_min, ind_shot_max, ind_SI_min, ind_SI_max, plot_factor):
    """
    Plot signal intensity for a specified range of shots and signal intensity indices.

    Parameters
    ----------
    s : ndarray
        2-D array of signals (e.g., time series) with shape (num_rows, num_shots).
    ind_shot_min : int
        Minimum shot index (inclusive, 0-based).
    ind_shot_max : int
        Maximum shot index (inclusive, 0-based).
    ind_SI_min : int or float
        Minimum signal intensity index.
    ind_SI_max : int or float
        Maximum signal intensity index.
    plot_factor : int or float
        Scaling factor applied to the signal before plotting.
    """
    # Ensure s is a NumPy array
    s = np.asarray(s)

    # MATLAB behaviour: if s is empty, do nothing
    if s.size == 0:
        return

    # Slice the specified range of shots (inclusive)
    # Python slice is exclusive at the end, hence +1
    s_slice = s[:, ind_shot_min : ind_shot_max + 1]

    # Compute the plotted signal values
    s_plot = s_slice * plot_factor + (ind_SI_min + ind_SI_max) / 2.0

    # Indices for plotting
    ind_plot = np.arange(ind_shot_min, ind_shot_max + 1)

    # Plot using the MATLAB-compatible plot function
    plot(ind_plot, s_plot, "r.-")
