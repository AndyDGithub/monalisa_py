from __future__ import annotations
import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import bmVarargin_kernelType_nWin_kernelParam


def bmGridder_n2u_leight(y, t, v, N_u, dK_u, kernelType=None, nWin=None, kernelParam=None, **kwargs):
    """
    Grid non-Cartesian data onto a Cartesian grid (density-compensated, leight variant).

    This function requires compiled MEX C extensions:
      - bmGridder_n2u_leight1_mex  (1-D)
      - bmGridder_n2u_leight2_mex  (2-D)
      - bmGridder_n2u_leight3_mex  (3-D)

    The C source files are located under:
      src/gridding123/mex/bmGridder_n2u_leight{1,2,3}/

    Compile per-platform instructions in the mex_command_*.txt files there.

    Parameters
    ----------
    y       : (nCh, nPt)  complex single - raw k-space data
    t       : (imDim, nPt) float         - k-space trajectory
    v       : (1, nPt)    float          - density compensation weights
    N_u     : array-like  [Nx, Ny, Nz]  - Cartesian grid size
    dK_u    : array-like  [dKx, dKy, dKz] - grid step
    kernelType  : str  ('gauss' or 'kaiser')
    nWin        : int  - kernel window width
    kernelParam : array-like - kernel parameters

    Returns
    -------
    data_u : (nCh, Nx, Ny, Nz) complex - gridded Cartesian data
    """
    raise NotImplementedError(
        "bmGridder_n2u_leight requires compiled MEX C extensions "
        "(bmGridder_n2u_leight1/2/3_mex). "
        "Compile from src/gridding123/mex/bmGridder_n2u_leight*/."
    )
