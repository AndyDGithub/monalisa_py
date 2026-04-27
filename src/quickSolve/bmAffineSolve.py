# Auto-generated from MATLAB source. Review manually before production use.

from src.fourierN.bmDFT import bmDFT
from third_part.matlab_compat.matlab_native import figure, imagesc, plot
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmAffineSolve(y, f, x):
    x, myPerm = np.sort(x)
    f = f[myPerm]

    if y >= f[-1]:
        mySlope = (f[-1] - f[-2])/(x[-1] - x[-2])
        myOffset = f[-1] - mySlope*x[-1]
    elif y <= f[0]:
        mySlope = (f[1] - f[0])/(x[1] - x[0])
        myOffset = f[0] - mySlope*x[0]
    else:
        myDiff = y - f
        myIndex = np.where(myDiff > 0)[0][-1]
        mySlope = (f[myIndex+1] - f[myIndex])/(x[myIndex+1] - x[myIndex])
        myOffset = f[myIndex] - mySlope*x[myIndex]

    out = (y - myOffset)/mySlope
    return out
