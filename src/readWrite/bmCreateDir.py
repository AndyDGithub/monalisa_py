from src.readWrite.bmCheckDir import bmCheckDir
import os
from src.arrayUtility.bmBlockReshape import bmBlockReshape

def bmCreateDir(argDir, varargin):
    myErrorFlag = False

    if len(varargin) > 0:
        myErrorFlag = varargin[0]

    out = 1

    if bmCheckDir(argDir, False):
        if myErrorFlag:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", "The directory already exists !")
        out = 0
        return out

    try:
        os.mkdir(argDir)
    except OSError:
        import tkinter.messagebox as msgbox
        msgbox.showerror("Error", "Unable to create the directory")
        out = 0
        return out

    if not bmCheckDir(argDir, 0):
        import tkinter.messagebox as msgbox
        msgbox.showerror("Error", "Unable to creat the directory")
        out = 0

    return out
