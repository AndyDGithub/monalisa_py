from __future__ import annotations
import numpy as np


def bmGridder_n2u(data_n, t, Dn, N_u, dK_u, kernelType=None, nWin=None, kernelParam=None, **kwargs):
    """
    Grid non-Cartesian data onto a Cartesian grid (original density-compensated variant).

    Requires compiled MEX C extensions. See src/gridding123/mex/ for build instructions.

    Parameters
    ----------
    data_n  : (nCh, nPt) complex single - raw k-space data
    t       : (imDim, nPt) float        - k-space trajectory
    Dn      : (1, nPt) float            - density weights
    N_u     : array-like [Nx, Ny, Nz]  - Cartesian grid size
    dK_u    : array-like [dKx,dKy,dKz] - grid step
    kernelType  : str
    nWin        : int
    kernelParam : array-like

    Returns
    -------
    data_u : (nCh, Nx, Ny, Nz) complex - gridded data
    """
    raise NotImplementedError(
        "bmGridder_n2u requires compiled MEX C extensions. "
        "See src/gridding123/mex/ for build instructions."
    )
