import numpy as np

def bmBump(x, xCut):
    xCut = np.abs(xCut)
    x = x / xCut
    n = np.abs(x)
    y = np.exp(-1./(1 - n**2)) * np.exp(1)
    y[n >= 1] = 0
    return y
