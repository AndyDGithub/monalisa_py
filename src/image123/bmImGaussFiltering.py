from src.image123.bmImDFT import bmImDFT
from src.image123.bmImIDF import bmImIDF
from src.image123.bmImReshape import bmImReshape
import numpy as np
from src.image123.bmImResize import bmBlockReshape

def normpdf(x, mu, sigma):
    coeff = 1 / (np.sqrt(2 * np.pi) * sigma)
    return coeff * np.exp(-0.5 * ((x - mu) / sigma)**2)


def bmImGaussFiltering(argIm, argSigma, blackBorder):
    [argIm, imDim, imSize_0] = bmImReshape(argIm)
    blackBorder = blackBorder.ravel().T

    if imDim == 1:
        [F, kx] = bmImDFT(argIm)
        [kx] = np.ndgrid(kx)
        n = np.sqrt(kx**2)
        FK = normpdf(n, 0, 1/2/np.pi/argSigma)
        F = F * FK
        out = bmImIDF(F).real
    elif imDim == 2:
        [F, kx, ky] = bmImDFT(argIm)
        [kx, ky] = np.ndgrid(kx, ky)
        n = np.sqrt(kx**2 + ky**2)
        FK = normpdf(n, 0, 1/2/np.pi/argSigma)
        F = F * FK
        out = bmImIDF(F).real
    elif imDim == 3:
        [F, kx, ky, kz] = bmImDFT(argIm)
        [kx, ky, kz] = np.ndgrid(kx, ky, kz)
        n = np.sqrt(kx**2 + ky**2 + kz**2)
        FK = normpdf(n, 0, 1/2/np.pi/argSigma)
        F = F * FK
        out = bmImIDF(F).real

    out = out / np.mean(out.ravel())

    if imDim == 2:
        out = out[blackBorder[0]:imSize_0[0,1] + blackBorder[0],
                  blackBorder[1]:imSize_0[0,2] + blackBorder[1]]
    elif imDim == 3:
        out = out[blackBorder[0]:imSize_0[0,1] + blackBorder[0],
                  blackBorder[1]:imSize_0[0,2] + blackBorder[1],
                  blackBorder[2]:imSize_0[0,3] + blackBorder[2]]

    return out
