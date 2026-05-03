from src.function1.bmBump import bmBump
import numpy as np
from src.image123.bmImDFT import bmImDFT
from src.image123.bmImIDF import bmImIDF

def bmImBumpFiltering(argIm, nPixFilter):
    """
    Apply a bump-filter to an image or volume using a 3D bump function.

    Parameters
    ----------
    argIm : ndarray
        Input image or volume.
    nPixFilter : int
        Filter width in pixels.

    Returns
    -------
    ndarray
        Filtered image with the same shape as ``argIm``.
    """
    myPlus = 10.0
    mySmall = 0.1

    myMean_0 = np.mean(argIm.ravel())
    plus_flag = False

    if abs(myMean_0) < mySmall:
        argIm = argIm + myPlus
        myMean_0 = np.mean(argIm.ravel())
        plus_flag = True

    argSize = argIm.shape

    # Mimic bmImReshape behaviour without importing the module
    imDim = argIm.ndim
    if imDim == 1:
        Nx, = argIm.shape
        Ny = Nz = 1
    elif imDim == 2:
        Nx, Ny = argIm.shape
        Nz = 1
    else:
        Nx, Ny, Nz = argIm.shape

    Nx_mid = np.floor(Nx / 2 + 1).astype(int)
    Ny_mid = np.floor(Ny / 2 + 1).astype(int) if Ny > 1 else 0
    Nz_mid = np.floor(Nz / 2 + 1).astype(int) if Nz > 1 else 0

    if imDim == 1:
        x = np.arange(1, Nx + 1) - Nx_mid
        n = np.sqrt(x ** 2)
        K = bmBump(n, nPixFilter)

    elif imDim == 2:
        x, y = np.meshgrid(np.arange(1, Nx + 1),
                           np.arange(1, Ny + 1),
                           indexing='ij')
        x = x - Nx_mid
        y = y - Ny_mid
        n = np.sqrt(x ** 2 + y ** 2)
        K = bmBump(n, nPixFilter)

    else:  # imDim == 3
        x, y, z = np.meshgrid(np.arange(1, Nx + 1),
                               np.arange(1, Ny + 1),
                               np.arange(1, Nz + 1),
                               indexing='ij')
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
    out = out / (np.mean(out.ravel()) * myMean_0)

    if plus_flag:
        out -= myPlus

    return out
