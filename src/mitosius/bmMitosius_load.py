import os
import numpy as np
import scipy.io

from src.arrayUtility.bmIndex2MultiIndex import bmIndex2MultiIndex


def bmMitosius_load(mitosius_dir, arg_name, *edge_args):
    """
    Load a variable from a mitosius directory structure.

    Port of MATLAB bmMitosius_load.m.

    Parameters
    ----------
    mitosius_dir : str
        Root directory of the mitosius structure.
    arg_name : str
        Variable name to load ('y', 't', or 've').
    *edge_args : optional
        One argument per mitosius dimension.  Each can be:
        - 'all'      → load every index along that dimension
        - int/array  → load only those 1-indexed positions

    Returns
    -------
    out : list
        Flat list of loaded arrays (in column-major order of the mitosius cell).
        If only one dimension of length 1 exists the list is squeezed to the
        elements directly.
    """
    size_mat = scipy.io.loadmat(os.path.join(mitosius_dir, "mitosius_size.mat"))
    in_mitosius_size = np.array(size_mat["mitosius_size"], dtype=np.float64).ravel()
    mitosius_ndims   = len(in_mitosius_size)

    # Build edge lists (1-indexed ranges per dimension)
    if len(edge_args) == 0:
        edge_list = [np.arange(1, int(s) + 1) for s in in_mitosius_size]
    else:
        if len(edge_args) != mitosius_ndims:
            raise ValueError(
                f"Expected {mitosius_ndims} edge arguments, got {len(edge_args)}."
            )
        edge_list = []
        for i, ea in enumerate(edge_args):
            if isinstance(ea, str) and ea == "all":
                edge_list.append(np.arange(1, int(in_mitosius_size[i]) + 1))
            else:
                ea_arr = np.array(ea, dtype=int).ravel()
                edge_list.append(ea_arr)

    out_mitosius_size = np.array([len(e) for e in edge_list], dtype=int)
    out_mitosius_length = int(np.prod(out_mitosius_size))

    out = [None] * out_mitosius_length

    for i in range(1, out_mitosius_length + 1):
        out_multi  = bmIndex2MultiIndex(i, out_mitosius_size)
        in_indices = np.array([edge_list[j][int(out_multi[j]) - 1]
                                for j in range(mitosius_ndims)], dtype=int)

        num_id   = "".join(f"_{int(idx)}" for idx in in_indices)
        mat_path = os.path.join(mitosius_dir, f"cell{num_id}", f"{arg_name}.mat")

        try:
            data = scipy.io.loadmat(mat_path)
        except Exception:
            import mat73
            data = mat73.loadmat(mat_path)

        key = [k for k in data.keys() if not k.startswith("_")][0]
        out[i - 1] = data[key]

    return out
