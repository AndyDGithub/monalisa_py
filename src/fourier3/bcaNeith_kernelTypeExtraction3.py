from src.geom123 import bmTraj

def bcaNeith_kernelTypeExtraction3(kspace, kernel):
    """
    Wrapper that mirrors the MATLAB function name used elsewhere.

    Parameters
    ----------
    kspace : np.ndarray
        4-D k-space array of shape (Nx, Ny, Nz, Ncoils).
    kernel : array-like
        Sequence of three odd integers [Nxk, Nyk, Nzk] describing the kerne
kernel size.

    Returns
    -------
    csr_matrix
        Sparse matrix of kernel masks.
    """
    return KernelTypeExtraction(kspace, kernel)
