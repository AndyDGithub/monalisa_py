import scipy.io

def bmLoad(arg_file):
    """
    Load data from a .mat file and return the first user-defined variable.

    Parameters
    ----------
    arg_file : str
        Path to the .mat file without extension.  The function appends ``.m
``.m
``.mat`` internally.

    Returns
    -------
    ndarray or other array-like
        The contents of the first variable stored in the MATLAB file.

    Raises
    ------
    ValueError
        If the file contains no user-defined variables.
    """
    mat_dict = scipy.io.loadmat(f"{arg_file}.mat", struct_as_record=False)

    # Filter out scipy.io metadata keys
    user_keys = [k for k in mat_dict if not k.startswith("__")]

    if not user_keys:
        raise ValueError("No data fields found in the .mat file.")

    return mat_dict[user_keys[0]]
