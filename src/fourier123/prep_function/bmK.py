import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.fourier3.bmDFT3 import bmDFT3
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import bmVarargin_kernelType_nWin_kernelParam


def bmK(N_u, dK_u, nCh, kernelType=None, nWin=None, kernelParam=None):
    """
    Generate the deapodization kernel K for Gaussian-gridded data.

    Port of MATLAB bmK.m.  K is the inverse of the Fourier transform of the
    gridding convolution kernel, cropped to the reconstruction grid size N_u
    and repeated for all nCh channels.

    Parameters
    ----------
    N_u        : array-like, [Nx, Ny, Nz]
    dK_u       : array-like, [dKx, dKy, dKz]
    nCh        : int  - number of coils/channels
    kernelType : str or None  ('gauss' default)
    nWin       : int or None  (3 default)
    kernelParam: array-like or None  ([0.61, 10] default for gauss)

    Returns
    -------
    K : ndarray, complex64, shape (Nx*Ny*Nz, nCh)
    """
    arg_osf = 2

    kernelType, nWin, kernelParam = bmVarargin_kernelType_nWin_kernelParam(
        kernelType, nWin, kernelParam)

    N_u  = np.array(np.round(N_u), dtype=np.int32).ravel()
    N_u  = np.float64(N_u)                         # match MATLAB double(int32(...))
    N_u_os = np.round(N_u * arg_osf).astype(int)   # oversampled grid size

    imDim = len(N_u)
    if imDim != 3:
        raise NotImplementedError("bmK currently only supports 3-D (imDim == 3).")

    dK_u = np.float64(np.float32(np.array(dK_u).ravel()))
    nWin = float(np.float64(np.float32(nWin)))
    kernelParam = np.float64(np.float32(np.atleast_1d(kernelParam)))
    nCh_f = float(np.float32(nCh))

    if np.any(np.mod(N_u, 2) > 0):
        raise ValueError("N_u must have all components even for the Fourier transform.")

    Nx_u, Ny_u, Nz_u = int(N_u[0]), int(N_u[1]), int(N_u[2])

    # Oversampled coordinate arrays (same range as MATLAB colon operator)
    # MATLAB: x = (-Nx_u*osf/2 : Nx_u*osf/2 - 1) / osf
    x_arr = np.arange(-Nx_u * arg_osf // 2, Nx_u * arg_osf // 2) / arg_osf
    y_arr = np.arange(-Ny_u * arg_osf // 2, Ny_u * arg_osf // 2) / arg_osf
    z_arr = np.arange(-Nz_u * arg_osf // 2, Nz_u * arg_osf // 2) / arg_osf

    x3d, y3d, z3d = np.meshgrid(x_arr, y_arr, z_arr, indexing='ij')
    d = np.sqrt(x3d.ravel() ** 2 + y3d.ravel() ** 2 + z3d.ravel() ** 2)
    d = d.reshape(N_u_os)

    # Gaussian kernel weights
    if kernelType == 'gauss':
        mySigma = float(kernelParam.ravel()[0])
        K_max   = float(kernelParam.ravel()[1])
        # normpdf(d, 0, sigma) = exp(-0.5*(d/sigma)^2) / (sigma * sqrt(2*pi))
        myWeight = np.exp(-0.5 * (d / mySigma) ** 2) / (mySigma * np.sqrt(2 * np.pi))
    elif kernelType == 'kaiser':
        myTau    = float(kernelParam.ravel()[0])
        myAlpha  = float(kernelParam.ravel()[1])
        K_max    = float(kernelParam.ravel()[2])
        I0alpha  = float(np.i0(myAlpha))
        w = np.maximum(1.0 - (d / myTau) ** 2, 0.0)
        myWeight = np.i0(myAlpha * np.sqrt(w)) / I0alpha
    else:
        raise ValueError(f"Unknown kernelType: {kernelType!r}")

    # Window masking: zero out weight outside [-nWin_half, +nWin_half]
    nWin_half = np.fix(nWin / 2)
    x_mask = (x3d < -nWin_half) | (x3d > nWin_half)
    y_mask = (y3d < -nWin_half) | (y3d > nWin_half)
    z_mask = (z3d < -nWin_half) | (z3d > nWin_half)
    myWeight[x_mask] = 0.0
    myWeight[y_mask] = 0.0
    myWeight[z_mask] = 0.0

    # DFT of the oversampled kernel  (bmDFT3 works on shape (Nxos,Nyos,Nzos,nCh))
    # Treat as single-channel
    myWeight_4d = myWeight[:, :, :, np.newaxis].astype(np.complex128)
    K_os = bmDFT3(myWeight_4d, N_u_os, 1.0 / N_u)   # (Nxos, Nyos, Nzos, 1)

    # Crop to N_u in the centre of the oversampled grid
    xc = N_u_os[0] // 2
    yc = N_u_os[1] // 2
    zc = N_u_os[2] // 2
    xh = Nx_u // 2
    yh = Ny_u // 2
    zh = Nz_u // 2

    K_crop = K_os[xc - xh : xc + xh, yc - yh : yc + yh, zc - zh : zc + zh, 0]

    # Final adjustments: abs(real), normalise, invert, clip
    K_crop = np.abs(np.real(K_crop))
    K_crop = K_crop / np.max(np.abs(K_crop.ravel()))
    K_crop = 1.0 / K_crop
    K_crop = np.minimum(K_crop, K_max)

    # Repeat for nCh channels → (Nx*Ny*Nz, nCh)
    # Use C-order flatten so that bmBlockReshape (which uses C-order reshape)
    # correctly maps K_out[k, ch] → K_reshaped[ix, iy, iz, ch].
    nCh_int = int(nCh)
    K_flat = K_crop.ravel(order='C')[:, np.newaxis]           # (Nx*Ny*Nz, 1)
    K_out  = np.tile(K_flat, (1, nCh_int)).astype(np.float32)  # (Nx*Ny*Nz, nCh)

    return K_out
