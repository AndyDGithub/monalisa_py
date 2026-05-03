from __future__ import annotations
import numpy as np
from src.fourier1.bmDFT1 import bmDFT1
from src.fourier2.bmDFT2 import bmDFT2
from src.fourier3.bmDFT3 import bmDFT3

# Authors:
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023


def bmK_bump(N_u):
    """Compute the bump-function deapodization kernel for non-Cartesian gridding.

    The bump function is exp(-1/(1-d^2)) * (|d| < 1), which is a smooth
    compactly-supported weight in the oversampled k-space grid. Its DFT gives
    the correction kernel K that compensates for the convolution broadening
    introduced by gridding.

    Parameters:
    N_u (array-like): Image space grid size (must have all-even components).

    Returns:
    K (ndarray, float32): Deapodization kernel, shape matching N_u spatial dims,
        values are 1/K_normalized so that multiplying by K undoes gridding blur.
    """
    arg_osf = 2  # oversampling factor

    N_u    = np.array(np.round(np.asarray(N_u).ravel()), dtype=np.int32).astype(float)
    N_u_os = np.round(N_u * arg_osf).astype(int)
    imDim  = len(N_u)

    if np.any(np.mod(N_u, 2) > 0):
        raise ValueError('N_u must have all components even for the Fourier transform.')

    Nx_u = int(N_u[0]) if imDim >= 1 else 0
    Ny_u = int(N_u[1]) if imDim >= 2 else 0
    Nz_u = int(N_u[2]) if imDim >= 3 else 0

    # Build the distance array d in the oversampled grid (normalised so that
    # d=1 corresponds to the edge of the support region)
    if imDim == 1:
        x_arr = np.arange(-Nx_u * arg_osf // 2, Nx_u * arg_osf // 2) / arg_osf
        d = np.abs(x_arr).reshape(N_u_os[0])
    elif imDim == 2:
        x_arr = np.arange(-Nx_u * arg_osf // 2, Nx_u * arg_osf // 2) / arg_osf
        y_arr = np.arange(-Ny_u * arg_osf // 2, Ny_u * arg_osf // 2) / arg_osf
        x2d, y2d = np.meshgrid(x_arr, y_arr, indexing='ij')
        d = np.sqrt(x2d ** 2 + y2d ** 2).reshape(N_u_os[:2])
    else:
        x_arr = np.arange(-Nx_u * arg_osf // 2, Nx_u * arg_osf // 2) / arg_osf
        y_arr = np.arange(-Ny_u * arg_osf // 2, Ny_u * arg_osf // 2) / arg_osf
        z_arr = np.arange(-Nz_u * arg_osf // 2, Nz_u * arg_osf // 2) / arg_osf
        x3, y3, z3 = np.meshgrid(x_arr, y_arr, z_arr, indexing='ij')
        d = np.sqrt(x3 ** 2 + y3 ** 2 + z3 ** 2).reshape(N_u_os[:3])

    # Bump function: exp(-1/(1-d^2)) inside the unit ball, 0 outside
    inside = np.abs(d) < 1.0
    with np.errstate(divide='ignore', invalid='ignore'):
        myWeight = np.where(inside, np.exp(-1.0 / np.where(inside, 1.0 - d ** 2, 1.0)), 0.0)
    myWeight[~inside] = 0.0

    # DFT functions expect a trailing channel dimension (..., nCh)
    myWeight_ch = myWeight[..., np.newaxis].astype(np.complex128)
    dK_u = 1.0 / N_u  # frequency step for the DFT (1/N_u per dimension)

    if imDim == 1:
        K = bmDFT1(myWeight_ch, N_u_os, dK_u)
    elif imDim == 2:
        K = bmDFT2(myWeight_ch, N_u_os, dK_u)
    else:
        K = bmDFT3(myWeight_ch, N_u_os, dK_u)

    # Crop the DFT result to N_u centered within the oversampled N_u_os grid
    if imDim == 1:
        x_center = N_u_os[0] // 2
        x_half   = Nx_u // 2
        K = K[x_center - x_half : x_center + x_half, 0]
    elif imDim == 2:
        xc, yc = N_u_os[0] // 2, N_u_os[1] // 2
        xh, yh = Nx_u // 2, Ny_u // 2
        K = K[xc - xh : xc + xh, yc - yh : yc + yh, 0]
    else:
        xc, yc, zc = N_u_os[0] // 2, N_u_os[1] // 2, N_u_os[2] // 2
        xh, yh, zh = Nx_u // 2, Ny_u // 2, Nz_u // 2
        K = K[xc - xh : xc + xh, yc - yh : yc + yh, zc - zh : zc + zh, 0]

    # Normalise and invert: K = single(1 / (real(K) / max(|real(K)|)))
    K = np.real(K)
    max_K = np.max(np.abs(K.ravel()))
    if max_K > 0:
        K = K / max_K
    K = np.float32(1.0 / np.maximum(K, 1e-10))

    return K
