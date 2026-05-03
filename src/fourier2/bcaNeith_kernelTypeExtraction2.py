from src.geom123 import bmTraj

def bcaNeith_kernelTypeExtraction2(kspace, kernel):
    """
    Extracts the types of kernels from the k-space.

    Parameters
    ----------
    kspace : array_like
        The k-space data array.
    kernel : array_like
        The kernel dimensions (typically a 2-element sequence).

    Returns
    -------
    ndarray
        Kernel types extracted from the k-space.

    Notes
    -----
    This function is a thin wrapper around :func:`bcaNeith_kernelTypeExtrac
:func:`bcaNeith_kernelTypeExtrac
:func:`bcaNeith_kernelTypeExtraction`
    to provide a stable API name that aligns with the MATLAB implementation
implementation
implementation.
    """
    return _core(kspace, kernel)
