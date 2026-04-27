from src.arrayUtility.bmCol import bmCol
from src.arrayUtility.bmIndex2MultiIndex import bmIndex2MultiIndex
import numpy as np

from third_part.matlab_compat.matlab_native import load, save

def e(mitosius_dir, file_name, var_name, arg_var, varargin):
    arg_var = arg_var.ravel()
    temp_load = load([mitosius_dir, "/mitosius_size"])
    mitosius_size = bmCol(temp_load.mitosius_size).T
    mitosius_ndims = np.shape(mitosius_size.ravel(), 1)
    mitosius_length = np.prod(mitosius_size.ravel())
    sub_mitosius_size = np.zeros(1, mitosius_ndims)

    # defining_edge_list_and_out_mitosius_size --------------------------------
    L = mitosius_ndims
    edge_list = cell(L, 1)
    for i in range(L):
        temp_edge = bmCol(varargin[i]).T
        edge_list[i] = temp_edge

    if len(edge_list) != mitosius_ndims:
        raise ValueError("The number of edges not compatible with mitosius_ndims.")

    sub_mitosius_length = np.prod(sub_mitosius_size.ravel())
    for i in range(sub_mitosius_length):
        subMultiIndex = bmIndex2MultiIndex(i, sub_mitosius_size)
        multiIndex = np.zeros(1, mitosius_ndims)
        for j in range(mitosius_ndims):
            multiIndex[j] = edge_list[j][0, subMultiIndex[0, j]]

        num_id = []
        for j in range(mitosius_ndims):
            num_id.append('_' + str(multiIndex[j]))
        num_id = ' '.join(num_id)

        curr_file = [mitosius_dir, "/cell", num_id, "/", file_name]
        curr_var = arg_var[i]
        curr_name = f"var_{var_name}_{num_id}"
        exec(f"{curr_name} = {curr_var}")

        save(curr_file, curr_name, "-v7.3")

    return bmMitosius_sav

def bmMitosius_save(mitosius_dir, file_name, var_name, arg_var, varargin):
    return e(mitosius_dir, file_name, var_name, arg_var, varargin)
