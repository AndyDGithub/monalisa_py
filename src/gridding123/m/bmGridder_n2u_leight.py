import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import bmVarargin_kernelType_nWin_kernelParam


def bmGridder_n2u_leight(y, t, v, N_u, dK_u,
                          kernelType=None, nWin=None, kernelParam=None):
    """
    Density-compensated non-Cartesian → Cartesian gridding (Gaussian kernel).

    Port of MATLAB bmGridder_n2u_leight.m (the MEX back-end is replaced by a
    pure-NumPy implementation that produces equivalent results).

    Parameters
    ----------
    y         : array (nCh, nPt) complex — non-Cartesian raw data
    t         : array (3, nPt) float    — trajectory (physical units)
    v         : array (1, nPt) float    — density-compensation weights
    N_u       : array-like [Nx, Ny, Nz]
    dK_u      : array-like [dKx, dKy, dKz]
    kernelType: str or None  ('gauss' default)
    nWin      : int or None  (3 default)
    kernelParam: array-like or None ([0.61, 10] default for gauss)

    Returns
    -------
    data_u : ndarray, complex64, shape (nCh, Nx, Ny, Nz)
    """
    _, nWin, kernelParam = bmVarargin_kernelType_nWin_kernelParam(
        kernelType, nWin, kernelParam)

    t = np.float32(bmPointReshape(t))   # (3, nPt)
    y = np.complex64(bmPointReshape(y)) # (nCh, nPt)
    v = np.float32(bmPointReshape(v))   # (1, nPt)  or (nPt,)

    nCh  = y.shape[0]
    nPt  = y.shape[1]
    imDim = t.shape[0]

    N_u  = np.array(N_u, dtype=np.float64).ravel()
    dK_u = np.array(dK_u, dtype=np.float64).ravel()
    nWin_f = float(nWin)
    kp   = np.float64(np.float32(np.atleast_1d(kernelParam)))

    # --- rescale trajectory ---------------------------------------------------
    # MATLAB shifts by fix(N/2 + 1) so trajectory values in [1, N] (1-indexed)
    Nx_u = int(N_u[0]);  Ny_u = int(N_u[1]);  Nz_u = int(N_u[2])

    tx = t[0, :].copy() / float(np.float32(dK_u[0]))
    ty = t[1, :].copy() / float(np.float32(dK_u[1]))
    tz = t[2, :].copy() / float(np.float32(dK_u[2]))

    v_sc = v.ravel().copy()
    v_sc = v_sc / float(np.float32(dK_u[0]))
    v_sc = v_sc / float(np.float32(dK_u[1]))
    v_sc = v_sc / float(np.float32(dK_u[2]))

    shift_x = int(np.fix(Nx_u / 2 + 1))
    shift_y = int(np.fix(Ny_u / 2 + 1))
    shift_z = int(np.fix(Nz_u / 2 + 1))

    tx = tx + shift_x   # now 1-indexed, centre at shift_x
    ty = ty + shift_y
    tz = tz + shift_z

    # --- remove out-of-box points -------------------------------------------
    mask = ((tx >= 1) & (tx <= Nx_u) &
            (ty >= 1) & (ty <= Ny_u) &
            (tz >= 1) & (tz <= Nz_u))

    tx   = tx[mask];   ty  = ty[mask];   tz  = tz[mask]
    y    = y[:, mask];  v_sc = v_sc[mask]
    nPt  = int(np.sum(mask))

    # --- Gaussian gridding kernel -------------------------------------------
    sigma = float(kp.ravel()[0])
    nWin_half = int(np.fix(nWin_f / 2))   # = 1 for nWin=3

    N_total = Nx_u * Ny_u * Nz_u

    data_u_re = np.zeros((nCh, N_total), dtype=np.float32)
    data_u_im = np.zeros((nCh, N_total), dtype=np.float32)

    # Round to nearest integer grid point (1-indexed)
    tx_r = np.round(tx).astype(np.int32)
    ty_r = np.round(ty).astype(np.int32)
    tz_r = np.round(tz).astype(np.int32)

    # normpdf(d, 0, sigma) = exp(-0.5*(d/sigma)^2) / (sigma*sqrt(2*pi))
    _inv_sig2 = np.float32(0.5 / (sigma * sigma))
    _norm     = np.float32(1.0 / (sigma * np.sqrt(2.0 * np.pi)))

    y_re = np.real(y)   # (nCh, nPt)
    y_im = np.imag(y)

    for dx in range(-nWin_half, nWin_half + 1):
        for dy in range(-nWin_half, nWin_half + 1):
            for dz in range(-nWin_half, nWin_half + 1):
                # 1-indexed grid position of this neighbour
                ix = tx_r + dx   # (nPt,)  1-indexed
                iy = ty_r + dy
                iz = tz_r + dz

                # distance in grid-units from actual trajectory to this neighbour
                d2 = ((tx - ix.astype(np.float32)) ** 2 +
                      (ty - iy.astype(np.float32)) ** 2 +
                      (tz - iz.astype(np.float32)) ** 2)
                gauss_w = _norm * np.exp(-_inv_sig2 * d2)   # (nPt,)

                # volume-compensated weight
                w = (v_sc * gauss_w).astype(np.float32)     # (nPt,)

                # bounds check (convert to 0-indexed)
                ix0 = ix - 1;  iy0 = iy - 1;  iz0 = iz - 1
                valid = ((ix0 >= 0) & (ix0 < Nx_u) &
                         (iy0 >= 0) & (iy0 < Ny_u) &
                         (iz0 >= 0) & (iz0 < Nz_u))

                # column-major (Fortran) linear index
                lin = np.where(valid,
                               ix0 + Nx_u * iy0 + Nx_u * Ny_u * iz0,
                               0).astype(np.int64)

                w_v = np.where(valid, w, np.float32(0.0))

                for ch in range(nCh):
                    wr = y_re[ch] * w_v
                    wi = y_im[ch] * w_v
                    data_u_re[ch] += np.bincount(lin, weights=wr,
                                                 minlength=N_total).astype(np.float32)
                    data_u_im[ch] += np.bincount(lin, weights=wi,
                                                 minlength=N_total).astype(np.float32)

    # reshape to (nCh, Nx, Ny, Nz) using F-order (column-major spatial)
    data_u = (data_u_re + 1j * data_u_im).reshape(nCh, Nx_u, Ny_u, Nz_u, order='F')
    return data_u
