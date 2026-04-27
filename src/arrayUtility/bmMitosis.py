import numpy as np
from src.arrayUtility.bmIndex2MultiIndex import bmIndex2MultiIndex


def bmMitosis(*args, n_tables):
    """
    Split tables according to binning masks.

    Mirrors MATLAB bmMitosis where nargout determines n_tables.

    Parameters
    ----------
    *args : arrays
        First n_tables are data tables; remaining are masks.
        Masks can also be passed as a single Python list as the last arg.
    n_tables : int (keyword-only)
        Number of input tables (== number of output values).

    Returns
    -------
    tuple of lists
        One list per table. Each list has N_tot entries (one per phase).

    Example
    -------
    y, t = bmMitosis(y_tot, t_tot, mask, n_tables=2)
    """
    nTable = int(n_tables)
    tables = list(args[:nTable])
    mask_args = list(args[nTable:])

    if not mask_args:
        raise ValueError("No masks provided")

    # A Python list as single arg = cell array of masks
    if len(mask_args) == 1 and isinstance(mask_args[0], list):
        masks = mask_args[0]
    else:
        masks = mask_args

    nMask = len(masks)
    nOfCol = np.asarray(tables[0]).shape[-1]

    in_size = []
    new_size = []
    for j in range(nTable):
        arr = np.asarray(tables[j])
        temp_shape = arr.shape
        in_size.append(temp_shape[:-1])
        nOfCol_j = temp_shape[-1]
        if nOfCol_j != nOfCol:
            raise ValueError("Last dimension mismatch between tables")
        flat = int(np.prod(temp_shape[:-1]))
        new_size.append((flat, nOfCol_j))

    for mask in masks:
        m = np.asarray(mask)
        if m.ndim != 2:
            raise ValueError("Each mask must be 2-D")
        if m.shape[-1] != nOfCol:
            raise ValueError("Mask column count does not match table last dimension")

    inTable = [np.asarray(tables[j]).reshape(new_size[j]) for j in range(nTable)]
    inMask = [np.asarray(m) for m in masks]
    nPhase = np.array([m.shape[0] for m in inMask], dtype=int)

    N_tot = int(np.prod(nPhase))

    # outTable_cell[i][j] = table j filtered by combined mask for phase i
    outTable_cell = [[None] * nTable for _ in range(N_tot)]

    for i in range(1, N_tot + 1):
        myIndex = bmIndex2MultiIndex(i, nPhase)
        myMask = np.ones(nOfCol, dtype=bool)
        for k in range(nMask):
            row = int(myIndex[k]) - 1
            myMask = myMask & (inMask[k][row, :] > 0)

        for j in range(nTable):
            temp_size = list(in_size[j]) + [int(np.sum(myMask))]
            outTable_cell[i - 1][j] = inTable[j][:, myMask].reshape(temp_size)

    # Return: one list per table (mirrors MATLAB varargout{j} = outTable_cell(:, j))
    return tuple([[outTable_cell[i][j] for i in range(N_tot)] for j in range(nTable)])
