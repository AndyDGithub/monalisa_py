import numpy as np
from src.arrayUtility import bmBlockReshape  # Import statement to resolve ModuleNotFoundError

def t(plotHandle, selectedBin, sequentialBinningMask, timestampMs):
    plotHandle.YData = sequentialBinningMask[selectedBin, :]
    plotHandle.Parent.Title.Text = f'Sequential Binning Mask: Bin {selectedBin}'
    return True  # Assuming a success return type

def updatePlot(plotHandle, selectedBin, sequentialBinningMask, timestampMs):
    return t(plotHandle, selectedBin, sequentialBinningMask, timestampMs)
