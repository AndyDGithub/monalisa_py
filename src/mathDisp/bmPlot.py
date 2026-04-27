from third_part.matlab_compat.matlab_native import plot
import numpy as np

def t(x, y, varargin):
    myLineType = ".-"
    if len(varargin) > 0:
        myLineType = varargin[0]
        if not myLineType or myLineType == 'hold':
            myLineType = ".-"
    myLineWidth = 2
    if len(varargin) > 1:
        myLineWidth = varargin[1]
        if not myLineWidth or not isinstance(myLineWidth, (int, float)):
            myLineWidth = 2
    myMarkerSize = 20
    if len(varargin) > 2:
        myMarkerSize = varargin[2]
        if not myMarkerSize or not isinstance(myMarkerSize, (int, float)):
            myMarkerSize = 20
    myColor = "b"
    if len(varargin) > 3:
        myColor = varargin[3]
        if not myColor or not isinstance(myColor, str):
            myColor = "b"

    notHoldOnFlag = True
    if len(varargin) > 0:
        if any('hold' in arg for arg in (varargin[0], varargin[-1])):
            notHoldOnFlag = False

    if notHoldOnFlag:
        import matplotlib.pyplot as plt
        plt.figure()
    else:
        plt.hold(True)

    plot(x, y, myLineType, markersize=myMarkerSize, linewidth=myLineWidth, color=myColor)
    plt.hold(False)
    return

def bmPlot(x, y, varargin):
    return t(x, y, varargin)
