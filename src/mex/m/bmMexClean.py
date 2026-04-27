from src.readWrite.bmDeleteFile import bmDeleteFile
from src.readWrite.bmDirList import bmDirList
from src.readWrite.bmNameList import bmNameList

from demo.script_demo.script_recon_calls.sheet_recon_calls_script import cd
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023
def n(varargin):
    argDir = "C:/main/matlab/bmToolBox"
    myOS = "windows"

    if not varargin:
        pass
    elif len(varargin) == 1:
        argDir = varargin[0]
        myOS = "windows"
    elif len(varargin) == 2:
        argDir = varargin[0]
        myOS = varargin[1]

    myCurrentDir = cd()
    myDirList = bmDirList(argDir, True) + [argDir]
    for i in range(len(myDirList)):
        cd(myDirList[i])
        myFileNameList = bmNameList(myDirList[i], False)
        for j in range(len(myFileNameList)):
            myFileName = myFileNameList[j]

            if len(myFileName) >= 7:
                if myFileName[-6:] == '.mexw64':
                    bmDeleteFile([myDirList[i], '/', myFileName])
                elif myFileName[-6:] == '.mexa64':
                    bmDeleteFile([myDirList[i], '/', myFileName])

    cd(myCurrentDir)
    return bmMexClean

def bmMexClean(varargin):
    return n(varargin)
