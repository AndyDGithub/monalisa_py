import numpy as np
from scipy.stats import norm

def bmGauss(x, mySigma, varargin):
    myMean = []
    if len(varargin) > 0:
        myMean = varargin[0]
    if myMean is None or myMean == []:
        myMean = 0

    y = norm.pdf(x, loc=myMean, scale=mySigma)
    return y
