from src.function1.bmBump import bmBump
import numpy as np
from src.image123.bmImDFT import bmImDFT
from src.image123.bmImIDF import bmImIDF
from src.image123.bmImReshape import bmImReshape


def bmImBumpFiltering(argIm, nPixFilter):
    myPlus = 10;  # -------------------------------------------------------------- magic number
    mySmall = 0.1;  # ------------------------------------------------------------- magic number

    myMean_0 = np.mean(argIm.ravel())
    plus_flag = False

    if abs(myMean_0) < mySmall:
        argIm += myPlus
        myMean_0 = np.mean(argIm.ravel())
        plus_flag = True

    argSize = np.shape(argIm)

    [argIm, imDim, _, Nx, Ny, Nz] = bmImReshape(argIm)

    Nx_mid = []
    Ny_mid = []
    Nz_mid = []

    if imDim == 1:
        Nx_mid = np.fix(Nx / 2 + 1)

        x = np.arange(1, Nx + 1) - Nx_mid
        n = np.sqrt(x ** 2)
        K = bmBump(n, nPixFilter)

    if imDim == 2:
        Nx_mid = np.fix(Nx / 2 + 1)
        Ny_mid = np.fix(Ny / 2 + 1)

        x, y = np.meshgrid(np.arange(1, Nx + 1), np.arange(1, Ny + 1))
        x = x - Nx_mid
        y = y - Ny_mid
        n = np.sqrt(x ** 2 + y ** 2)
        K = bmBump(n, nPixFilter)

    if imDim == 3:
        Nx_mid = np.fix(Nx / 2 + 1)
        Ny_mid = np.fix(Ny / 2 + 1)
        Nz_mid = np.fix(Nz / 2 + 1)

        x, y, z = np.meshgrid(np.arange(1, Nx + 1), np.arange(1, Ny + 1), np.arange(1, Nz + 1))
        x = x - Nx_mid
        y = y - Ny_mid
        z = z - Nz_mid
        n = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        K = bmBump(n, nPixFilter)

    FK = bmImDFT(K)
    out = bmImDFT(argIm)
    out *= FK
    out = np.real(bmImIDF(out))
    out = np.reshape(out, argSize)
    out /= np.mean(out.ravel()) * myMean_0

    if plus_flag:
        out -= myPlus

    return out
