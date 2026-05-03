from src.sparseMat.m.bmSparseMat import bmSparseMat
from src.sparseMat.m.bmSparseMat_vec import int32
# Import the helper that converts a directory path to a binary array.
from src.readWrite.bmBinary2Array import bmBinary2Array


def _read_header(file_path: str):
    """
    Read a header file consisting of whitespace-separated strings.
    Returns a list of strings, equivalent to MATLAB's textread with '%s'.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content.split()


def _str2num(s: str):
    """
    Convert a string to a numeric value, mirroring MATLAB's str2num.
    Handles integer and floating-point representations.
    """
    try:
        # Attempt integer conversion first for efficiency.
        return int(s)
    except ValueError:
        return float(s)


def bmBinary2Array_sparseMat(argDir: str) -> bmSparseMat:
    """
    Load a sparse matrix description from a binary directory.

    Parameters
    ----------
    argDir : str
        Path to the directory containing the binary files and header.

    Returns
    -------
    bmSparseMat
        An instance populated with the sparse matrix metadata and data.
    """
    s = bmSparseMat()

    header_path = f"{argDir}/bmArray2Binary_sparseMat_header.txt"
    myCell = _read_header(header_path)

    # MATLAB indexing starts at 1; Python is 0-based.
    s.type = myCell[0]

    if s.type in ("matlab_ind", "l_squeezed_matlab_ind"):
        s.block_type = myCell[1]
        s.kernel_type = myCell[2]
        s.r_size = int32(_str2num(myCell[3]))
        s.l_size = int32(_str2num(myCell[4]))
        s.l_nJump = int32(_str2num(myCell[5]))

        s.r_nJump = bmBinary2Array(argDir, "r_nJump")
        s.r_ind = bmBinary2Array(argDir, "r_ind")
        s.m_val = bmBinary2Array(argDir, "m_val")
        s.l_ind = bmBinary2Array(argDir, "l_ind")
        s.N_u = bmBinary2Array(argDir, "N_u")
        s.d_u = bmBinary2Array(argDir, "d_u")
        s.nWin = bmBinary2Array(argDir, "nWin")
        s.kernelParam = bmBinary2Array(argDir, "kernelParam")

    elif s.type in ("cpp_prepared", "l_squeezed_cpp_prepared"):
        s.block_type = myCell[1]
        s.kernel_type = myCell[2]
        s.r_size = int32(_str2num(myCell[3]))
        s.l_size = int32(_str2num(myCell[4]))
        s.l_nJump = int32(_str2num(myCell[5]))
        s.nBlock = int64(_str2num(myCell[6]))

        s.r_nJump = bmBinary2Array(argDir, "r_nJump")
        s.r_jump = bmBinary2Array(argDir, "r_jump")
        s.m_val = bmBinary2Array(argDir, "m_val")
        s.l_jump = bmBinary2Array(argDir, "l_jump")
        s.N_u = bmBinary2Array(argDir, "N_u")
        s.d_u = bmBinary2Array(argDir, "d_u")
        s.nWin = bmBinary2Array(argDir, "nWin")
        s.kernelParam = bmBinary2Array(argDir, "kernelParam")

        s.block_length = bmBinary2Array(argDir, "block_length")
        s.l_block_start = bmBinary2Array(argDir, "l_block_start")
        s.m_block_start = bmBinary2Array(argDir, "m_block_start")

    return s
