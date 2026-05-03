from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty
from porting.lib.utils import errordlg
from src.readWrite.bmCheckDir import bmCheckDir


def bmCreateDir(argDir, varargin):
    """Create a directory; return 1 on success, 0 if it already exists or on error."""
    myErrorFlag = False
    if not isempty(varargin):
        myErrorFlag = varargin[0]

    out = 1
    if bmCheckDir(argDir, False):
        if myErrorFlag:
            errordlg('The directory already exists !')
        out = 0
        return out

    try:
        import os
        os.mkdir(argDir)
    except OSError as e:
        errordlg(f'Unable to create the directory: {e}')
        out = 0
        return out

    if not bmCheckDir(argDir, False):
        errordlg('Unable to create the directory')
        out = 0
        return out

    return out
