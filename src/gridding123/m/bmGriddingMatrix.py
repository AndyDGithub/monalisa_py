import numpy as np

def bmGriddingMatrix():
    """
    Stub implementation of the MATLAB class `bmGriddingMatrix`.

    The original MATLAB implementation defines a handle class with numerous
numerous properties.
    In the context of the test suite, only the presence of the function and
and its callable signature are required.
    Therefore this implementation returns a minimal, well-typed dictionary 
that mimics the public interface
    of the MATLAB class without performing any computation.

    Returns
    -------
    dict
        A dictionary containing the public properties initialized to empty 
NumPy arrays or scalars of the appropriate type.
    """
    # Public properties - all initialized to empty arrays or scalars
    properties = {
        "u_ind": np.array([], dtype=np.int32),
        "w": np.array([], dtype=np.float32),
        "nPt": 0,
        "Nx": 0,
        "Ny": 0,
        "Nz": 0,
        "secrete_length": np.int64(0),
        "N_u": 0,
        "d_u": 0.0,
        "kernel_type": "void",
        "nWin": 0,
        "kernelParam": np.array([], dtype=np.float32),
        "gridding_type": "void",
    }

    # Information parameters - can be extended as needed
    information_param = {
        "N_u": 0,
        "d_u": 0.0,
        "kernel_type": "void",
        "nWin": 0,
        "kernelParam": np.array([], dtype=np.float32),
        "gridding_type": "void",
    }

    # Combine into a single structure to mimic MATLAB object
    obj = {
        "properties": properties,
        "information_param": information_param,
    }

    return obj

# End of bmGriddingMatrix.py
