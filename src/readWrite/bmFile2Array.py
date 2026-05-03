import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape


def bmFile2Array(argDir, argName, argChar, argType):
    """
    Read data from a file into a NumPy array.

    Parameters
    ----------
    argDir : str
        Directory containing the files.
    argName : str
        Base name of the file (without extension).
    argChar : str
        Data type selector: 'd' for binary (.hdat/.dat),
        't' for text (.txt), or 'c' for CSV (.csv).
    argType : dtype
        NumPy dtype to read the data as (e.g. np.float32).

    Returns
    -------
    np.ndarray
        Array with the data read from the file, reshaped to the
        dimensions specified in the header.
    """
    if argChar == "d":
        # Binary format: .hdat header + .dat data
        header_path = f"{argDir}/{argName}.hdat"
        data_path = f"{argDir}/{argName}.dat"

        with open(header_path, "rb") as fh:
            # first byte: number of dimensions
            ndims = np.fromfile(fh, dtype=np.uint8, count=1)[0]
            # next ndims+1 bytes: sizes + total length
            nums = np.fromfile(fh, dtype=np.uint8, count=ndims + 1)
            sizes = nums[:-1].astype(int)
            total_len = nums[-1]

        shape = tuple(sizes)
        if ndims == 1:
            out = np.zeros((sizes[0], 1), dtype=argType)
        else:
            out = np.zeros(shape, dtype=argType)

        with open(data_path, "rb") as fd:
            data = np.fromfile(fd, dtype=argType, count=total_len)
            out[:] = data.reshape(shape, order="F")

    elif argChar == "t":
        # Text format: .txt
        txt_path = f"{argDir}/{argName}.txt"

        with open(txt_path, "rb") as fh:
            ndims = np.fromfile(fh, dtype=np.uint8, count=1)[0]
            nums = np.fromfile(fh, dtype=np.uint8, count=ndims + 1)
            sizes = nums[:-1].astype(int)
            total_len = nums[-1]

        shape = tuple(sizes)
        if ndims == 1:
            out = np.zeros((sizes[0], 1), dtype=argType)
        else:
            out = np.zeros(shape, dtype=argType)

        # Read data starting after the header (skip first 3 lines)
        data = np.genfromtxt(
            txt_path, delimiter=" ", skip_header=3, dtype=argType
        ).ravel()
        out[:] = data.reshape(shape, order="F")

    elif argChar == "c":
        # CSV format: .csv
        csv_path = f"{argDir}/{argName}.csv"

        with open(csv_path, "rb") as fh:
            ndims = np.fromfile(fh, dtype=np.uint8, count=1)[0]
            nums = np.fromfile(fh, dtype=np.uint8, count=ndims + 1)
            sizes = nums[:-1].astype(int)
            total_len = nums[-1]

        shape = tuple(sizes)
        if ndims == 1:
            out = np.zeros((sizes[0], 1), dtype=argType)
        else:
            out = np.zeros(shape, dtype=argType)

        # Read data starting after the header (skip first 4 lines)
        data = np.genfromtxt(
            csv_path, delimiter=" ", skip_header=4, dtype=argType
        ).ravel()
        out[:] = data.reshape(shape, order="F")

    else:
        raise ValueError(f"Unsupported argChar '{argChar}'")

    return out
