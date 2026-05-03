from __future__ import annotations
import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape

def bmImDeformField2sparseMat_ind_weight(v, N_u, Dn, torus_flag):
    v   = np.asarray(bmPointReshape(v), dtype=float)
    Dn  = np.asarray(Dn, dtype=float).ravel() if Dn is not None and len(np.atleast_1d(Dn)) > 0 else None
    N_u = np.asarray(N_u, dtype=float).ravel()

    imDim = v.shape[0]
    nPt   = v.shape[1]

    if nPt != int(np.prod(N_u)):
        raise ValueError('bmImDeformField2sparseMat_ind_weight: deformation field must have as many vectors as pixels/voxels.')

    N_u_int = N_u.astype(int)
    Nx_u = N_u_int[0] if imDim >= 1 else 0
    Ny_u = N_u_int[1] if imDim >= 2 else 0
    Nz_u = N_u_int[2] if imDim >= 3 else 0

    # Build grid + trajectory
    if imDim == 1:
        x_u = np.arange(1, Nx_u + 1, dtype=float)
        t   = x_u.reshape(1, -1) + v
    elif imDim == 2:
        x_u, y_u = np.meshgrid(np.arange(1, Nx_u+1), np.arange(1, Ny_u+1), indexing='ij')
        t = np.vstack([x_u.ravel(), y_u.ravel()]) + v
    else:  # imDim == 3
        x_u, y_u, z_u = np.meshgrid(np.arange(1, Nx_u+1), np.arange(1, Ny_u+1), np.arange(1, Nz_u+1), indexing='ij')
        t = np.vstack([x_u.ravel(), y_u.ravel(), z_u.ravel()]) + v

    deleteMask = np.zeros(nPt, dtype=bool)
    if imDim >= 1:
        deleteMask |= (t[0, :] < 1) | (t[0, :] > Nx_u)
    if imDim >= 2:
        deleteMask |= (t[1, :] < 1) | (t[1, :] > Ny_u)
    if imDim >= 3:
        deleteMask |= (t[2, :] < 1) | (t[2, :] > Nz_u)

    # Neighbor offsets: [0,1] per dim
    grids = [np.array([0, 1], dtype=float)] * imDim
    mesh  = np.meshgrid(*grids, indexing='ij')
    c     = np.vstack([m.ravel() for m in mesh])  # (imDim, nNb)
    nNb   = c.shape[1]

    # Expand c and t_floor/t_rest over nPt
    c_exp = c[:, :, np.newaxis]  # (imDim, nNb, 1)
    t_floor = np.floor(t)        # (imDim, nPt)
    t_rest  = t - t_floor
    t_floor_exp = t_floor[:, np.newaxis, :]  # (imDim, 1, nPt)
    t_rest_exp  = t_rest[:, np.newaxis, :]   # (imDim, 1, nPt)

    d = t_rest_exp - c_exp  # (imDim, nNb, nPt)
    d_sq = np.sum(d ** 2, axis=0)  # (nNb, nPt)
    d_norm = np.sqrt(d_sq)

    # Bump function
    inside = np.abs(d_norm) < 1.0
    with np.errstate(divide='ignore', invalid='ignore'):
        bump = np.where(inside, np.exp(-1.0 / np.where(inside, 1.0 - d_norm**2, 1.0)), 0.0)
    bump[~inside] = 0.0
    myWeight = bump.reshape(nNb, nPt)  # (nNb, nPt)

    if Dn is not None:
        Dn_rep = np.tile(Dn.reshape(1, nPt), (nNb, 1))  # (nNb, nPt)
        myWeight = myWeight * Dn_rep
    else:
        Dn_rep = None

    # Compute flat 1-based indices with torus wrap
    n = (t_floor_exp + c_exp).astype(float)  # (imDim, nNb, nPt)
    if imDim >= 1:
        n[0] = np.mod(n[0] - 1, Nx_u) + 1
    if imDim >= 2:
        n[1] = np.mod(n[1] - 1, Ny_u) + 1
    if imDim >= 3:
        n[2] = np.mod(n[2] - 1, Nz_u) + 1

    if imDim == 1:
        flat_n = n[0]  # (nNb, nPt)
    elif imDim == 2:
        flat_n = 1 + (n[0] - 1) + (n[1] - 1) * Nx_u
    else:
        flat_n = 1 + (n[0] - 1) + (n[1] - 1) * Nx_u + (n[2] - 1) * Nx_u * Ny_u

    if not torus_flag:
        flat_n[:, deleteMask]   = 0
        myWeight[:, deleteMask] = 0.0
        if Dn_rep is not None:
            Dn_rep[:, deleteMask] = 0.0

        keep = ~deleteMask
        flat_n   = flat_n[:, keep]
        myWeight = myWeight[:, keep]
        if Dn_rep is not None:
            Dn_out = Dn_rep[:, keep].ravel().astype(float)
        else:
            Dn_out = np.array([], dtype=float)

        ind_2 = np.repeat(np.where(keep)[0] + 1, nNb).astype(float)  # 1-based
    else:
        if Dn_rep is not None:
            Dn_out = Dn_rep.ravel().astype(float)
        else:
            Dn_out = np.array([], dtype=float)
        ind_2 = np.tile(np.arange(1, nPt + 1), (nNb, 1)).T.ravel().astype(float)

    ind_1        = flat_n.ravel().astype(float)
    myWeight_out = myWeight.ravel().astype(float)

    return ind_1, ind_2, myWeight_out, Dn_out
