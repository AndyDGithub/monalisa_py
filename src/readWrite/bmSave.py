import scipy.io
from third_part.matlab_compat.matlab_runtime_metadata import resolve_inputname


def bmSave(arg_file, arg_var, *, var_name=None):
    my_name = resolve_inputname(
        2,
        args=(arg_file, arg_var),
        explicit_name=var_name,
        fallback_name="arg_var",
        frame_depth=2,
    )
    scipy.io.savemat(arg_file, {my_name: arg_var})
    return None
