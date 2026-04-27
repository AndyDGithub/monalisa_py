"""Lightweight scipy-backed sparse matrix for Python MRI gridding."""

import numpy as np
import scipy.sparse as sp


class bmSparseMatScipy:
    """
    Thin wrapper around a scipy sparse matrix that exposes the same
    interface attributes as MATLAB's bmSparseMat class.

    Attributes
    ----------
    matrix : scipy.sparse.csr_matrix
        The actual sparse gridding matrix.
    N_u : ndarray, shape (imDim,)
        Grid dimensions [Nx, Ny, Nz].
    d_u : ndarray, shape (imDim,)
        Grid spacing [dKx, dKy, dKz] (= 1/FoV per axis).
    kernel_type : str
        Gridding kernel type ('gauss' or 'kaiser').
    nWin : float
        Gridding window width.
    kernelParam : ndarray
        Kernel parameters.
    r_size : int
        Number of trajectory points (columns of the Gn matrix).
    """

    def __init__(self, matrix, N_u, dK_u, kernelType='gauss', nWin=3, kernelParam=None):
        if not sp.issparse(matrix):
            raise TypeError("matrix must be a scipy sparse matrix")
        self.matrix = matrix.tocsr()
        self._N_u = np.asarray(N_u, dtype=np.float64).ravel()
        self._d_u = np.asarray(dK_u, dtype=np.float64).ravel()
        self.kernel_type = kernelType
        self.nWin = float(nWin)
        self.kernelParam = np.asarray(kernelParam, dtype=np.float64) if kernelParam is not None else None
        # nPt = number of columns (trajectory points) for Gn, or rows for Gu
        self._nPt = matrix.shape[1]

    @property
    def N_u(self):
        return self._N_u

    @property
    def d_u(self):
        return self._d_u

    @property
    def r_size(self):
        return self._nPt

    def __repr__(self):
        return (f"<bmSparseMatScipy shape={self.matrix.shape} "
                f"N_u={self._N_u} kernel={self.kernel_type}>")
