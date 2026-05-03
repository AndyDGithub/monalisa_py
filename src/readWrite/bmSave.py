from third_part.matlab_compat.matlab_runtime_metadata import resolve_inputname
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np
import scipy.io
from third_part.matlab_compat.matlab_runtime_metadata import resolve_inputn
resolve_inputname


def bmSave(arg_file, arg_var):
    """
    Save a variable to a .mat file under the name of the input variable.

    Parameters
    ----------
    arg_file : str
        Path to the .mat file where the variable will be saved.
    arg_var : Any
        The variable to save.

    Notes
    -----
    This mirrors the MATLAB behaviour of ``inputname(2)``: the name of the
    second input argument (`arg_var`) is stored in the file.  If the name
    cannot be resolved, ``arg_var`` is used as the variable name.
    """
    my_name = resolve_inputname(
        2,
        args=(arg_file, arg_var),
        explicit_name=None,
        fallback_name="arg_var",
        frame_depth=2,
    )
    scipy.io.savemat(arg_file, {my_name: arg_var})
    return None
