from __future__ import annotations
import numpy as np
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import bmVarargin_kernelType_nWin_kernelParam

def bmK_old(N_u, dK_u, nCh, varargin=None):
    if varargin is None:
        varargin = ()
    if isinstance(varargin, (list, tuple)) and len(varargin) >= 3:
        kernelType, nWin, kernelParam = varargin[0], varargin[1], varargin[2]
    else:
        kernelType, nWin, kernelParam = None, None, None

    kernelType, nWin, kernelParam = bmVarargin_kernelType_nWin_kernelParam(kernelType, nWin, kernelParam)

    N_u   = np.float64(np.float32(np.asarray(N_u).ravel()))
    dK_u  = np.float64(np.float32(np.asarray(dK_u).ravel()))
    nWin  = float(np.float64(np.float32(nWin)))
    kernelParam = np.float64(np.float32(np.atleast_1d(kernelParam)))
    nCh   = float(np.float32(nCh))
    imDim = len(N_u)

    if np.any(np.mod(N_u, 2) > 0):
        raise ValueError('N_u must have all components even for the Fourier transform.')

    Nu_tot = int(np.prod(N_u))
    K = np.zeros(Nu_tot, dtype=np.float64)

    myTrajPoint = (np.fix(N_u / 2) + 1).astype(int)  # 1-based center

    nWin_int = int(np.fix(nWin / 2))
    myWin = np.arange(-nWin_int, nWin_int + 1)

    if imDim == 1:
        cx_arr = myWin.reshape(1, -1)
        c = cx_arr  # (1, nNb)
    elif imDim == 2:
        cx, cy = np.meshgrid(myWin, myWin, indexing='ij')
        c = np.vstack([cx.ravel(), cy.ravel()])
    else:
        cx, cy, cz = np.meshgrid(myWin, myWin, myWin, indexing='ij')
        c = np.vstack([cx.ravel(), cy.ravel(), cz.ravel()])

    n = c + myTrajPoint.reshape(-1, 1)

    # Mask out-of-bound
    nMask = np.zeros(c.shape[1], dtype=bool)
    if imDim >= 1:
        nMask |= (n[0, :] < 1) | (n[0, :] > N_u[0])
    if imDim >= 2:
        nMask |= (n[1, :] < 1) | (n[1, :] > N_u[1])
    if imDim >= 3:
        nMask |= (n[2, :] < 1) | (n[2, :] > N_u[2])

    n_valid = n[:, ~nMask]
    myDiff  = myTrajPoint.reshape(-1, 1) - n_valid
    d = np.sqrt(np.sum(myDiff.astype(float) ** 2, axis=0))

    if kernelType == 'gauss':
        mySigma  = float(kernelParam.ravel()[0])
        myWeight = np.exp(-0.5 * (d / mySigma) ** 2) / (mySigma * np.sqrt(2 * np.pi))
    elif kernelType == 'kaiser':
        myTau    = float(kernelParam.ravel()[0])
        myAlpha  = float(kernelParam.ravel()[1])
        I0alpha  = float(np.i0(myAlpha))
        w = np.maximum(1.0 - (d / myTau) ** 2, 0.0)
        myWeight = np.i0(myAlpha * np.sqrt(w)) / I0alpha
    else:
        raise ValueError(f'Unknown kernelType: {kernelType}')

    # Compute 0-based linear index into K
    if imDim == 1:
        myIndexList = (n_valid[0, :] - 1).astype(int)
    elif imDim == 2:
        myIndexList = (n_valid[0, :] - 1 + (n_valid[1, :] - 1) * N_u[0]).astype(int)
    else:
        myIndexList = (n_valid[0, :] - 1 + (n_valid[1, :] - 1) * N_u[0] + (n_valid[2, :] - 1) * N_u[0] * N_u[1]).astype(int)

    K[myIndexList] = myWeight
    K = K.reshape(list(N_u.astype(int)) + [1] if imDim < 3 else N_u.astype(int).tolist())

    # Per-dimension IFFT (MATLAB: fftshift(ifft(ifftshift(...)))*N*dK)
    for dim in range(imDim):
        K = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(K, axes=dim), axis=dim), axes=dim)
        K = K * N_u[dim] * dK_u[dim]

    K = np.real(K).ravel()
    max_K = np.max(np.abs(K))
    if max_K > 0:
        K = K / max_K
    K = np.float32(1.0 / np.maximum(K, 1e-10))
    K = np.tile(K.reshape(-1, 1), (1, int(nCh))).astype(np.float32)
    return K
