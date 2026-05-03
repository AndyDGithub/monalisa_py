import numpy as np

def bmCell2TextFile(arg_cell, arg_file):
    """
    Write a list of string items to a text file, each on its own line, unti
until 
until 
until a sentinel value is encountered.

    Parameters
    ----------
    arg_cell : list[str]
        List of strings to write to the file.
    arg_file : str
        Path to the output text file.

    Notes
    -----
    The MATLAB version writes each string to the file and stops when the ne
next element in the 
cell array is equal to -1.  This Python implementation follows the same log
logic, writing each 
string on a separate line except for the final entry before the sentinel, w
which is written 
without a trailing newline.
    """
    with open(arg_file, 'w') as fid:
        for idx, item in enumerate(arg_cell):
            # Stop when the next element is the sentinel
            if idx + 1 < len(arg_cell) and arg_cell[idx + 1] == -1:
                fid.write(str(item))
                break
            else:
                fid.write(f"{item}\n")
    return None
