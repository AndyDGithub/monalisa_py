from src.readWrite.bmDirList import bmDirList
from src.mex.m.bmMex_cell2command import bmMex_cell2command
from src.mex.m.bmMex_extern_dir import bmMex_extern_dir
import numpy as np
from src.readWrite.bmTextFile2Cell import bmTextFile2Cell
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape from arrayUtility module


def x(argDir, varargin):
    myOS = "windows"
    mex_dir_file = [argDir, "/bmMex/txt/bmMex_dir_blanc.txt"]

    if len(varargin) > 0:
        myOS = varargin[0]
        mex_dir_file = [argDir, "/bmMex/txt/bmMex_dir_blanc.txt"] + tuple(varargin[1:])

    cuda_I_dir = []
    cuda_L_dir = []
    fftw_I_dir = []
    fftw_L_dir = []

    if mex_dir_file:
        cuda_I_dir, cuda_L_dir, fftw_I_dir, fftw_L_dir = bmMex_extern_dir(mex_dir_file)

    myCurrentDir = np.getcwd()
    myDirList = np.concatenate((np.array([argDir]), bmDirList(argDir, True)))

    for i in range(len(myDirList)):
        np.chdir(myDirList[i])

        if myOS == 'windows':
            command_file = [myDirList[i], "/mex_command_windows.txt"]
        elif myOS == 'linux':
            command_file = [myDirList[i], "/mex_command_linux.txt"]

        if np.exists(command_file):
            text_cell = bmTextFile2Cell(command_file)
            myCommand, myCommand_flag = bmMex_cell2command(text_cell, cuda_I_dir, cuda_L_dir, fftw_I_dir, fftw_L_dir)

            if myCommand_flag:
                print(myCommand)  # Using print instead of MATLAB's disp
                exec(myCommand)

    np.chdir(myCurrentDir)


def bmMex(argDir, varargin):
    return x(argDir, varargin)
