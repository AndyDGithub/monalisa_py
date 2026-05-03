# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

# myPlus = 10;  # magic number
# mySmall = 0.1;  # magic number

from src.image123.bmImDFT import bmImDFT
from src.image123.bmImIDF import bmImIDF
from src.image123.bmImReshape import bmImReshape
import numpy as np
from scipy.stats import norm

def bmImContrastEnhance(argIm, enhence_factor):
    """
    Enhance image contrast using a Gaussian weighting in the frequency doma
domain.

    Parameters
    ----------
    argIm : np.ndarray
        Input image array.
    enhence_factor : float
        Contrast enhancement factor.

    Returns
    -------
    np.ndarray
        Contrast-enhanced image.
    """
    myPlus = 10
    mySmall = 0.1

    argIm, imDim, _ = bmImReshape(argIm)

    myMean_0 = np.mean(argIm.ravel())
    plus_flag = False
    if abs(myMean_0) < mySmall:
        argIm += myPlus
        myMean_0 = np.mean(argIm.ravel())
        plus_flag = True

    if imDim == 1:
        F, kx = bmImDFT(argIm)
        kx_grid = np.meshgrid(kx, indexing="ij")[0]
        n = np.abs(kx_grid)
    elif imDim == 2:
        F, kx, ky = bmImDFT(argIm)
        kx_grid, ky_grid = np.meshgrid(kx, ky, indexing="ij")
        n = np.sqrt(kx_grid**2 + ky_grid**2)
    elif imDim == 3:
        F, kx, ky, kz = bmImDFT(argIm)
        kx_grid, ky_grid, kz_grid = np.meshgrid(kx, ky, kz, indexing="ij")
        n = np.sqrt(kx_grid**2 + ky_grid**2 + kz_grid**2)
    else:
        raise ValueError(f"Unsupported image dimensionality: {imDim}")

    FK = 1.0 / norm.pdf(n, 0.0, 1.0 / np.log(enhence_factor))
    F *= FK
    out = np.abs(bmImIDF(F))
    out = out / np.mean(out.ravel()) * myMean_0

    if plus_flag:
        out -= myPlus

    return out



# Dummy implementation to satisfy imports
# File: src/geom123/bmTraj.py
# --------------------------------------------------------------
# This module provides a placeholder `bmTraj` function to allow
# modules that import it to be loaded successfully. The actual
# functionality is not required for the current unit tests.

def bmTraj(*args, **kwargs):
    """
    Placeholder for the MATLAB function `bmTraj`. It returns None
    and accepts any arguments. This is sufficient for importing
    modules that depend on `bmTraj` without providing the full
    implementation.
    """
    return None
