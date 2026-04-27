from src.readWrite.bmCheckDir import bmCheckDir
import numpy as np
import os

def bmNameList(argDir, varargin):
    if not bmCheckDir(argDir, False):
        return []

    myList = [f for f in os.listdir(argDir) if os.path.isfile(os.path.join(argDir, f)) or os.path.islink(os.path.join(argDir, f))]
    out = [os.path.basename(i) for i in myList]

    N = len(out)
    if varargin and varargin[0]:
        for i in range(N):
            new_dir = os.path.join(argDir, out[i])
            out += bmNameList(new_dir, True)

    return out
