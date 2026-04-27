from src.readWrite.bmNameList import bmNameList
import os
import numpy as np
try:
    from src.readWrite.bmCheckDir import bmCheckDir
    from src.readWrite.bmGetDir import bmGetDir
except ImportError:
    pass  # Handle missing imports in the calling environment

def bmDicomInfo(varargin):
    myFile = 0
    myDir = 0
    myPath = 0
    myFileName = 0
    myDirName = 0
    dirFlag = 0
    pathFlag = 0
    fileFlag = 0

    if len(varargin) == 0:
        [myDir, myPath, _] = bmGetDir()
        dirFlag = 1
        if isinstance(myDir, (int, float)):
            return []

    elif len(varargin) > 0:
        if len(varargin) > 2:
            raise ValueError("Wrong list of arguments")

        for i in range(0, len(varargin), 2):
            switch_val = varargin[i]

            if switch_val == 'Dir':
                myDir = varargin[i + 1]
                dirFlag = 1

            elif switch_val == 'Path':
                myPath = varargin[i + 1]
                pathFlag = 1

            elif switch_val == 'File':
                myFile = varargin[i + 1]
                fileFlag = 1

            else:
                raise ValueError("Wrong list of arguments")

    if dirFlag:
        myPath = os.path.join(myDir, '\\')
    elif pathFlag:
        myDir = os.path.dirname(myPath)
    elif fileFlag:
        myDir = os.path.dirname(myFile)
        myPath = os.path.join(myDir, '\\')
    else:
        raise ValueError("Directory or file not specified")

    if not bmCheckDir(myDir):
        return []

    if fileFlag:
        dicomInfo = pydicom.dcmread(myFile)
        return [dicomInfo]

    myFileNameList = bmNameList(myDir)
    myFileNameList = sorted(myFileNameList)

    if not myFileNameList:
        return []

    numOfImages = len(myFileNameList)
    dicomInfo = []

    for i in range(numOfImages):
        dicom_file_path = os.path.join(myPath, myFileNameList[i])
        dicomInfo.append(pydicom.dcmread(dicom_file_path))

    return dicomInfo
