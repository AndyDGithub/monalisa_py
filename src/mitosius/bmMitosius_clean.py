from src.readWrite.bmDeleteFile import bmDeleteFile
from src.readWrite.bmNameList import bmNameList
import numpy as np
from src.readWrite.bmCheckFile import bmCheckFile
from src.arrayUtility import bmBlockReshape  # Import bmBlockReshape here to fix ModuleNotFoundError

def n(mitosius_dir, varargin):
    nName = len(varargin)
    nameList = []

    mitosius_nameList = bmNameList(cell_dir=mitosius_dir, check_exist=False)
    mitosius_nameList = mitosius_nameList.ravel()
    iMax = np.shape(mitosius_nameList.ravel(), 1)

    continue_flag = True

    for i in range(iMax):
        if len(mitosius_nameList[i]) >= len('cell_') and mitosius_nameList[i].startswith('cell_'):
            continue_flag = False
            break

    if continue_flag:
        return

    cell_dir = [mitosius_dir, "/cell_", str(i)]
    cell_nameList = bmNameList(cell_dir=cell_dir, check_exist=False)
    cell_nName = np.shape(cell_nameList.ravel(), 1)

    for j in range(cell_nName):
        temp_name = cell_nameList[j]
        temp_file = [cell_dir, '/', temp_name]

        if len(temp_name) >= len('slurm') and temp_name.startswith('slurm'):
            if bmCheckFile(temp_file):
                bmDeleteFile(temp_file)

    for k in range(nName):
        for j in range(cell_nName):
            temp_name = cell_nameList[j]
            temp_file = [cell_dir, '/', temp_name]

            if temp_name == varargin[k]:
                if bmCheckFile(temp_file):
                    bmDeleteFile(temp_file)

def bmMitosius_clean(mitosius_dir, varargin):
    return n(mitosius_dir, varargin)
