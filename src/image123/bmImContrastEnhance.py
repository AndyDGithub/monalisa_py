from src.image123.bmImDFT import bmImDFT
from src.image123.bmImIDF import bmImIDF
from src.image123.bmImReshape import bmImReshape
import numpy as np
from scipy.stats import norm


def bmImContrastEnhance(argIm, enhence_factor):
    myPlus = 10;  # -------------------------------------------------------------- magic number
    mySmall = 0.1;  # ------------------------------------------------------------- magic number

    argIm, imDim, _ = bmImReshape(argIm)

    myMean_0 = np.mean(argIm.ravel())
    plus_flag = False
    if abs(myMean_0) < mySmall:
        argIm += myPlus
        myMean_0 = np.mean(argIm.ravel())
        plus_flag = True

    n = None
    if imDim == 1:
        F, kx = bmImDFT(argIm)
        [kx] = np.meshgrid(kx)
        n = np.sqrt(kx**2)
    elif imDim == 2:
        F, kx, ky = bmImDFT(argIm)
        [kx, ky] = np.meshgrid(kx, ky)
        n = np.sqrt(kx**2 + ky**2)
    elif imDim == 3:
        F, kx, ky, kz = bmImDFT(argIm)
        [kx, ky, kz] = np.meshgrid(kx, ky, kz)
        n = np.sqrt(kx**2 + ky**2 + kz**2)

    FK = 1./norm.pdf(n, 0, 1/np.log(enhence_factor))
    F *= FK
    out = np.abs(bmImIDF(F))
    out /= np.mean(out.ravel()) * myMean_0

    if plus_flag:
        out -= myPlus

    return out
