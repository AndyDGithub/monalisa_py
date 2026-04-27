import tkinter.filedialog as tkfd
import os

def bmGetFile():
    failFlag = 0
    myFileName = 0
    myPath = 0

    [myFileName, myPath] = tkfd.askopenfilename()

    if isinstance(myFileName, (int, float)):
        failFlag = 1
    if isinstance(myPath, (int, float)):
        failFlag = 1

    if failFlag:
        varargout = [0, 0, 0, 0, 0]
        return varargout

    myDir = os.path.dirname(myPath)
    myFile = os.path.join(myPath, myFileName)

    if not os.path.isdir(myDir):
        failFlag = 1
    if not os.path.isfile(myFile):
        failFlag = 1

    if failFlag:
        varargout = [0, 0, 0, 0, 0]
        return varargout

    myDirName = os.path.basename(myDir)

    varargout = [myFile, myDir, myPath, myFileName, myDirName]
    return varargout
