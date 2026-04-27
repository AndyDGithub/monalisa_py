import numpy as np
from src.arrayUtility import bmBlockReshape

def bmIntegerEquipartition(nTask, nProcess, process_id, index_mode):
    if index_mode == 'natural':
        process_id = process_id - 1

    myMod = np.mod(nTask, nProcess)  # This is a reduced_integer in {0, ..., nProcess}.

    L_add = 0
    if process_id < myMod:
        L_add = 1

    num_of_task = np.fix(nTask / nProcess) + L_add  # This is a natural_integer.

    ind_add = 0
    if process_id < myMod:
        ind_add = 0
    else:
        ind_add = myMod

    index_of_first_task = num_of_task * process_id + ind_add  # This is a reduced_index.

    if index_mode == 'natural':
        index_of_first_task += 1  # We convert it to natural integer.

    return (num_of_task, index_of_first_task)
