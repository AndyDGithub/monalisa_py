import numpy as np

def bmMex_cell2command(c, cuda_I_dir, cuda_L_dir, fftw_I_dir, fftw_L_dir):
    """
    Generate a command line string for mex compilation.

    Parameters
    ----------
    c : array_like
        Cell array (or list) of command components.  It may contain
        placeholder strings such as ``cuda_I_dir`` that are replaced by the
the
        corresponding directory arguments.  The cell may also contain a 

sentinel
        value ``-1`` which terminates the command string construction.
    cuda_I_dir : str or None
        Include ``-I"<cuda_I_dir>"`` in the command.
    cuda_L_dir : str or None
        Include ``-L"<cuda_L_dir>"`` in the command.
    fftw_I_dir : str or None
        Include ``-I"<fftw_I_dir>"`` in the command.
    fftw_L_dir : str or None
        Include ``-L"<fftw_L_dir>"`` in the command.

    Returns
    -------
    myCommand : str
        The assembled command line string.
    myCommand_flag : bool
        ``True`` if all required directories were supplied; ``False`` if an
an
        directory argument was missing, in which case ``myCommand`` is an
an empty string.
    """
    # Ensure 1-D sequence
    c = np.ravel(c)
    myCommand_flag = True

    # Pre-process: remove trailing '...' and leading spaces
    processed = []
    for item in c:
        if isinstance(item, str):
            s = item.strip()
            if len(s) > 3 and s.endswith("..."):
                s = s[:-3]
            processed.append(s)
        else:
            processed.append(item)

    # Substitution
    for i, item in enumerate(processed):
        if item == "cuda_I_dir":
            if not cuda_I_dir:
                myCommand_flag = False 
                return "", myCommand_flag
            processed[i] = f'-I"{cuda_I_dir}"'
        elif item == "cuda_L_dir":
            if not cuda_L_dir:
                myCommand_flag = False 
                return "", myCommand_flag
            processed[i] = f'-L"{cuda_L_dir}"'
        elif item == "fftw_I_dir":
            if not fftw_I_dir:
                myCommand_flag = False 
                return "", myCommand_flag
            processed[i] = f'-I"{fftw_I_dir}"'
        elif item == "fftw_L_dir":
            if not fftw_L_dir:
                myCommand_flag = False 
                return "", myCommand_flag
            processed[i] = f'-L"{fftw_L_dir}"'

    # Assemble command until sentinel -1
    parts = []
    for item in processed:
        if item == -1:
            break
        parts.append(str(item))
    myCommand = " ".join(parts)
    return myCommand, myCommand_flag
