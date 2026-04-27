import numpy as np
from src.arrayUtility import bmBlockReshape

def bmMex_cell2command(c, cuda_I_dir, cuda_L_dir, fftw_I_dir, fftw_L_dir):
    myCommand = []
    myCommand_flag = True

    c = c.ravel()

    # deleting '...' at end of lines
    for i in range(len(c)):
        if len(c[i]) > 3:
            if c[i][-3:] == '...':
                c[i] = c[i][:-3]

    # deleting white spaces at start of lines
    for i in range(len(c)):
        if c[i]:
            while c[i].startswith(' '):
                c[i] = c[i][1:]

    # substitution
    for i in range(len(c)):
        if isinstance(c[i], str) and c[i] == 'cuda_I_dir':
            if not cuda_I_dir:
                myCommand_flag = False
                myCommand = []
                return (myCommand, myCommand_flag)
            c[i] = f"-I\"{cuda_I_dir}\" "

        elif isinstance(c[i], str) and c[i] == 'cuda_L_dir':
            if not cuda_L_dir:
                myCommand_flag = False
                myCommand = []
                return (myCommand, myCommand_flag)
            c[i] = f"-L\"{cuda_L_dir}\" "

        elif isinstance(c[i], str) and c[i] == 'fftw_I_dir':
            if not fftw_I_dir:
                myCommand_flag = False
                myCommand = []
                return (myCommand, myCommand_flag)
            c[i] = f"-I\"{fftw_I_dir}\" "

        elif isinstance(c[i], str) and c[i] == 'fftw_L_dir':
            if not fftw_L_dir:
                myCommand_flag = False
                myCommand = []
                return (myCommand, myCommand_flag)
            c[i] = f"-L\"{fftw_L_dir}\" "

    myCommand = [item for sublist in c for item in (sublist if isinstance(sublist, list) else [sublist])]
    return (myCommand, myCommand_flag)
