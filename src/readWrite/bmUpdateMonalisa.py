from src.readWrite.bmCheckFile import bmCheckFile
from src.readWrite.bmDeleteFile import bmDeleteFile
from src.readWrite.bmDirList import bmDirList
from src.readWrite.bmNameList import bmNameList
import numpy as np
from shutil import copyfile

def a(dir_bmToolBox, dir_monalisa):
    L_bm = np.shape(dir_bmToolBox.ravel(), 1)
    L_ml = np.shape(dir_monalisa.ravel(), 1)
    rel_dirList = bmDirList(dir_monalisa, True)
    nDir = np.shape(rel_dirList.ravel(), 1)

    for i in range(nDir):
        temp_rel_dir = rel_dirList[i]
        ml_temp_dir = [dir_monalisa, temp_rel_dir]
        bm_temp_dir = [dir_bmToolBox, temp_rel_dir]

        temp_name_list = bmNameList(ml_temp_dir)

        for j in range(np.shape(temp_name_list, 1)):
            temp_name = temp_name_list[j]
            ml_temp_file = [ml_temp_dir, "/", temp_name]
            bm_temp_file = [bm_temp_dir, "/", temp_name]

            if bmCheckFile(ml_temp_file, False):
                bmDeleteFile(ml_temp_file)

            if bmCheckFile(bm_temp_file, False):
                copyfile(bm_temp_file, ml_temp_file)

def bmUpdateMonalisa(dir_bmToolBox, dir_monalisa):
    return a(dir_bmToolBox, dir_monalisa)
