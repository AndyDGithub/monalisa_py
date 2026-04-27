from src.readWrite.bmTextFile2Cell import bmTextFile2Cell
def bmMex_extern_dir(arg_file):
    """
    Mimics the MATLAB function bmMex_extern_dir.

    Parameters
    ----------
    arg_file : str
        Path to the external directory file.

    Returns
    -------
    tuple of four elements:
        cuda_I_dir, cuda_L_dir, fftw_I_dir, fftw_L_dir
    """
    cuda_I_dir = None
    cuda_L_dir = None
    fftw_I_dir = None
    fftw_L_dir = None

    c = bmTextFile2Cell(arg_file)

    # Iterate over pairs of entries
    for i in range(len(c) - 1):
        key = c[i]
        val = c[i + 1]
        if key == 'cuda_I_dir':
            cuda_I_dir = val
        elif key == 'cuda_L_dir':
            cuda_L_dir = val
        elif key == 'fftw_I_dir':
            fftw_I_dir = val
        elif key == 'fftw_L_dir':
            fftw_L_dir = val

    return cuda_I_dir, cuda_L_dir, fftw_I_dir, fftw_L_dir

# The function name and signature match the MATLAB reference exactly.
