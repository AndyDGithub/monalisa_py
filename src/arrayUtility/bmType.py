import numpy as np


def bmType(a):
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
