import numpy as np
from scipy.interpolate import RegularGridInterpolator


def bmImResize(argIm, n_u, N_u, interp_option='cubic'):
    """
    Resize an image (or coil-sensitivity map) from n_u to N_u using
    cubic interpolation on a periodic grid.

    Port of MATLAB bmImResize.m.

    Parameters
    ----------
    argIm        : array, shape (*n_u, nCh)  or column layout (prod(n_u)*nCh,)
    n_u          : array-like, source grid size [nx, ny, nz]
    N_u          : array-like, target grid size [Nx, Ny, Nz]
    interp_option: str, interpolation method ('cubic', 'linear', …)

    Returns
    -------
    outIm : ndarray, shape (*N_u, nCh), same dtype as argIm
    """
    N_u = np.array(N_u).ravel().astype(int)
    n_u = np.array(n_u).ravel().astype(int)
    imDim = len(n_u)

    if imDim != len(N_u):
        raise ValueError('n_u and N_u must correspond to the same image dimension.')

    argIm = np.asarray(argIm)
    nCh = int(argIm.size // int(np.prod(n_u)))
    myIm = argIm.reshape(tuple(n_u) + (nCh,))

    is_complex = not np.isrealobj(myIm)
    out_dtype = myIm.dtype
    outIm = np.zeros(tuple(N_u) + (nCh,), dtype=out_dtype)

    # Periodic extension: append first slice along each spatial axis
    # MATLAB: myIm = cat(1, myIm, myIm(1,:,:,:)); etc.
    for ax in range(imDim):
        idx = [slice(None)] * myIm.ndim
        idx[ax] = slice(0, 1)
        myIm = np.concatenate([myIm, myIm[tuple(idx)]], axis=ax)
    # myIm now has shape (n_u[0]+1, ..., n_u[imDim-1]+1, nCh)

    # Source 1-D coordinate grids (linspace(0,1, n_u[i]+1))
    grid_1d = tuple(np.linspace(0.0, 1.0, int(n_u[i]) + 1) for i in range(imDim))

    # Target 1-D coordinate grids: mod(0.5 + (-N/2 : N/2-1)/N, 1)
    query_1d = tuple(
        np.mod(0.5 + np.arange(-int(N_u[i]) // 2, int(N_u[i]) // 2) / int(N_u[i]), 1.0)
        for i in range(imDim)
    )

    # Build ND query meshgrid with ij-indexing (= MATLAB ndgrid)
    query_grids = np.meshgrid(*query_1d, indexing='ij')  # each (N_u[0], N_u[1], ...)
    query_pts = np.stack([g.ravel() for g in query_grids], axis=-1)  # (N_tot, imDim)

    for i in range(nCh):
        if is_complex:
            vals_re = myIm[..., i].real.astype(np.float64)
            vals_im = myIm[..., i].imag.astype(np.float64)
            interp_re = RegularGridInterpolator(grid_1d, vals_re, method=interp_option,
                                                bounds_error=False, fill_value=None)
            interp_im = RegularGridInterpolator(grid_1d, vals_im, method=interp_option,
                                                bounds_error=False, fill_value=None)
            result = (interp_re(query_pts) + 1j * interp_im(query_pts)).astype(out_dtype)
        else:
            vals = myIm[..., i].astype(np.float64)
            interp = RegularGridInterpolator(grid_1d, vals, method=interp_option,
                                             bounds_error=False, fill_value=None)
            result = interp(query_pts).astype(out_dtype)
        outIm[..., i] = result.reshape(tuple(N_u))

    return outIm
