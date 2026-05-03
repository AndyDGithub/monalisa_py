import numpy as np

# Import bmRotation3 from src.linAlg3
from src.linAlg3.bmRotation3 import bmRotation3

def bmType(a):
    """
    Determine the MATLAB-compatible type string of a NumPy array.

    Parameters
    ----------
    a : np.ndarray
        Input array.

    Returns
    -------
    str or None
        One of "real_double", "complex_double", "real_single", "complex_sin
"complex_single",
        or None if the type is unsupported.
    """
    a = np.asarray(a)
    is_complex = np.iscomplexobj(a)
    if not is_complex and a.dtype == np.float64:
        return "real_double"
    elif is_complex and a.dtype == np.complex128:
        return "complex_double"
    elif not is_complex and a.dtype == np.float32:
        return "real_single"
    elif is_complex and a.dtype == np.complex64:
        return "complex_single"
    return None
