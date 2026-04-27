import numpy as np

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.coilSense.map.bmCoilSense_pinv import bmCoilSense_pinv
from src.fourier3.bmIDF3 import bmIDF3
from src.fourier123.prep_function.bmK import bmK
from src.gridding123.m.bmGridder_n2u_leight import bmGridder_n2u_leight
from src.image123.bmImCrope import bmImCrope
from src.traj123.bmTraj_N_u_dK_u import bmTraj_N_u_dK_u
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import bmVarargin_kernelType_nWin_kernelParam


def bmMathilda(y, t, v,
               C=None, N_u=None, n_u=None, dK_u=None,
               kernelType=None, nWin=None, kernelParam=None,
               fft_lib_flag=None, leight_flag=None):
    """
    Gridded reconstruction of non-Cartesian MRI data.

    Port of MATLAB bmMathilda.m.

    1. Density-compensated gridding (Gaussian kernel) → Cartesian k-space
    2. 3-D centered iFFT
    3. Deapodization
    4. Coil combination via pseudo-inverse (if C is provided)

    Parameters
    ----------
    y           : (nCh, nPt) complex  — non-Cartesian raw data
    t           : (3, nPt)   float    — k-space trajectory
    v           : (1, nPt)   float    — density-compensation weights
    C           : array or None       — coil-sensitivity maps
    N_u         : array-like or None  — Cartesian grid size [Nx, Ny, Nz]
    n_u         : array-like or None  — output image size (= N_u if None)
    dK_u        : array-like or None  — Cartesian grid step [dKx, dKy, dKz]
    kernelType  : str or None         — 'gauss' (default) or 'kaiser'
    nWin        : int or None         — kernel window width (default 3)
    kernelParam : array-like or None  — kernel params (default [0.61, 10])
    fft_lib_flag: str or None         — reserved; only 'MATLAB' supported
    leight_flag : bool or None        — if False use deprecated gridder (unsupported)

    Returns
    -------
    x : ndarray, complex64, shape (Nx, Ny, Nz) or (Nx, Ny, Nz, nCh)
    """
    # --- defaults -------------------------------------------------------------
    if fft_lib_flag is None:
        fft_lib_flag = 'MATLAB'
    if leight_flag is None:
        leight_flag = True
    if not leight_flag:
        raise NotImplementedError("bmGridder_n2u (non-leight) is deprecated and not implemented.")

    # --- parse kernel params --------------------------------------------------
    kernelType, nWin, kernelParam = bmVarargin_kernelType_nWin_kernelParam(
        kernelType, nWin, kernelParam)

    # --- derive N_u / dK_u from trajectory if not provided -------------------
    N_u, dK_u = bmTraj_N_u_dK_u(t, N_u, dK_u)

    if n_u is None or (hasattr(n_u, '__len__') and len(n_u) == 0):
        n_u = N_u

    # --- validate dimensions --------------------------------------------------
    N_u_arr  = np.array(N_u, dtype=np.float64).ravel()
    n_u_arr  = np.array(n_u, dtype=np.float64).ravel()
    dK_u_arr = np.array(dK_u, dtype=np.float64).ravel()

    if np.any(np.mod(N_u_arr, 2) > 0):
        raise ValueError("N_u must have all components even for the Fourier transform.")

    # --- reshape inputs -------------------------------------------------------
    t_2d = np.float64(bmPointReshape(t))         # (3, nPt)
    y_2d = np.complex64(bmPointReshape(y))        # (nCh, nPt)
    v_2d = np.float64(bmPointReshape(v))          # (1, nPt)

    # MATLAB: if size(y,1) >= size(y,2): y = y.'
    if y_2d.shape[0] >= y_2d.shape[1]:
        y_2d = y_2d.T

    imDim = t_2d.shape[0]    # 3 for 3-D
    nCh   = y_2d.shape[0]

    N_u_int  = np.int32(np.round(N_u_arr)).tolist()
    n_u_int  = np.int32(np.round(n_u_arr)).tolist()
    dK_u_s   = np.float64(np.float32(dK_u_arr))   # match MATLAB double(single(...))
    N_u_s    = np.float32(N_u_arr)

    print(" ")
    print("This is Mathilda...  ")
    print(f"Matrix size  {N_u_s} . ")
    print(f"FoV          {1.0 / np.float32(dK_u_s)} . ")
    print(" ")

    # --- gridding: non-Cartesian → Cartesian k-space -------------------------
    x = bmGridder_n2u_leight(
        y_2d, t_2d, v_2d, N_u_arr, dK_u_s,
        kernelType=kernelType, nWin=nWin, kernelParam=kernelParam)
    # x: (nCh, Nx, Ny, Nz)

    # --- reorder to (Nx, Ny, Nz, nCh) for IDF and deapodization --------------
    x = np.moveaxis(x, 0, -1)   # (Nx, Ny, Nz, nCh)

    # --- 3-D inverse FFT ------------------------------------------------------
    x = bmIDF3(x, N_u_int, dK_u_s)   # (Nx, Ny, Nz, nCh)

    # --- deapodization --------------------------------------------------------
    K = bmK(N_u_s, np.float32(dK_u_s), nCh,
             kernelType=kernelType, nWin=nWin, kernelParam=kernelParam)
    # K: (Nx*Ny*Nz, nCh)
    K = bmBlockReshape(K, N_u_int)    # (Nx, Ny, Nz, nCh)
    x = np.complex64(x) * np.complex64(K)

    # --- crop if needed -------------------------------------------------------
    if not np.array_equal(N_u_arr, n_u_arr):
        x = bmImCrope(x, N_u_int, n_u_int)

    # --- coil combination -----------------------------------------------------
    if C is not None:
        C_arr = np.complex64(C)
        x = bmCoilSense_pinv(C_arr, x, n_u_int)

    return x
