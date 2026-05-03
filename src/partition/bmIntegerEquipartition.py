#
# index_mode must be 'reduced' or 'natural'. 

import numpy as np


def bmIntegerEquipartition(nTask, nProcess, process_id, index_mode):
    """
    EQUIPARTITION OF A TASK SET ACROSS PROCESSORS.

    Parameters
    ----------
    nTask : int
        Number of tasks to be distributed. Must be a natural integer.
    nProcess : int
        Number of processors available. Must be a natural integer.
    process_id : int
        Process identifier. If 'index_mode' is 'natural', it should be a 
        natural integer. If 'index_mode' is 'reduced', it should be a 
        reduced integer (i.e., in {0, ..., nProcess-1}).
    index_mode : str
        Mode for the process_id. Can be either 'natural' or 'reduced'.

    Returns
    -------
    num_of_task : int
        Number of tasks assigned to each processor.
    index_of_first_task : int
        Index of the first task that the current processor should handle.
    """
    # Convert to reduced index if using natural numbering
    if index_mode == 'natural':
        process_id -= 1

    myMod = nTask % nProcess

    L_add = 1 if process_id < myMod else 0

    num_of_task = (nTask // nProcess) + L_add

    ind_add = 0 if process_id < myMod else myMod

    index_of_first_task = num_of_task * process_id + ind_add

    if index_mode == 'natural':
        index_of_first_task += 1

    return int(num_of_task), int(index_of_first_task)
