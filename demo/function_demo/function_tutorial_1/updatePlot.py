import numpy as np

def t(plotHandle, selectedBin, sequentialBinningMask, timestampMs):
    """Update the plot based on the selected bin and sequential binning mas
mask.

    Args:
        plotHandle (object): The handle to the plot object.
        selectedBin (int): The index of the selected bin.
        sequentialBinningMask (np.ndarray): A binary mask indicating sequen
sequential binning.
        timestampMs (float): The current timestamp in milliseconds.

    Returns:
        None
    """
    return updatePlot(plotHandle, selectedBin, sequentialBinningMask)

# Auto-generated entrypoint alias for import compatibility
updatePlot = t
