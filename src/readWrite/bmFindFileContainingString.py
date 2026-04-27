import os
import re
from src.readWrite.bmCheckFile import bmCheckFile
from src.readWrite.bmDirList import bmDirList
from src.readWrite.bmNameList import bmNameList

def g(argDir, argString):
    myDirList = bmDirList(argDir, True)
    nDir = len(myDirList)

    for i in range(nDir):
        myNameList = bmNameList(myDirList[i])
        nName = len(myNameList)

        for j in range(nName):
            tempFile = os.path.join(myDirList[i], myNameList[j])
            if bmCheckFile(tempFile, False):
                with open(tempFile, 'r') as temp_fid:
                    myFind = []
                    myFind_flag = False

                    while True:
                        line = temp_fid.readline()
                        if not line:
                            break

                        myFind = [m.start() for m in re.finditer(argString, line)]
                        if any(f is not None for f in myFind):
                            myFind_flag = True

    return myFind_flag

def bmFindFileContainingString(argDir, argString):
    g(argDir, argString)
